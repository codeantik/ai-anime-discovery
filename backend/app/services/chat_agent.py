"""LangGraph conversational preference agent — Phase 4.

Multi-turn chat: the model gathers anime preferences across turns, can call
Tavily for live web context (e.g. "what's airing this season"), and calls the
existing recommend service once it has enough signal to produce picks.
"""

import json
import logging
from typing import Any, TypedDict

import numpy as np
from openai import AsyncOpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL, TAVILY_API_KEY
from app.models.recommend import RecommendRequest
from app.services import recommend as recommend_svc

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 4

SYSTEM_PROMPT = """You are an enthusiastic, knowledgeable anime recommendation assistant.

Your job: have a natural conversation to learn the user's taste (genres, mood, \
themes, preferred era, episode length, anime they already love), then call the \
get_recommendations tool to fetch real picks from the catalog and present them \
conversationally with the given reasons.

Guidelines:
- Ask at most 1-2 short clarifying questions before recommending — don't \
interrogate the user. If they've given you anything to go on, it's fine to \
recommend right away.
- Use web_search only when you need live/current information (e.g. what's \
airing this season, recent reviews) — not for general anime knowledge you \
already know.
- Once get_recommendations returns results, summarize them naturally in your \
reply; don't just dump JSON. Mention title and why it fits.
- Never invent anime that isn't in the tool results."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the live web for current anime info (e.g. what's airing this season, recent reviews).",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recommendations",
            "description": "Fetch ranked anime recommendations from the catalog based on the user's stated preferences.",
            "parameters": {
                "type": "object",
                "properties": {
                    "genres": {"type": "array", "items": {"type": "string"}},
                    "mood": {"type": "string"},
                    "themes": {"type": "array", "items": {"type": "string"}},
                    "era": {"type": "string", "enum": ["any", "classic", "2000s", "2010s", "recent"]},
                    "length": {"type": "string", "enum": ["any", "movie", "short", "season", "long"]},
                    "loved_titles": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
]


class ChatState(TypedDict):
    messages: list[dict[str, Any]]
    recommendations: list[dict]
    rounds: int


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=OPENAI_API_KEY)


async def _run_web_search(query: str) -> str:
    if not TAVILY_API_KEY:
        return "Web search is unavailable right now (no API key configured)."
    try:
        from tavily import AsyncTavilyClient

        client = AsyncTavilyClient(api_key=TAVILY_API_KEY)
        result = await client.search(query, max_results=5, search_depth="basic")
        snippets = [
            f"- {r['title']}: {r.get('content', '')[:300]}"
            for r in result.get("results", [])
        ]
        return "\n".join(snippets) if snippets else "No results found."
    except Exception as e:
        logger.warning(f"Tavily search failed: {e}")
        return f"Web search failed: {e}"


async def _run_get_recommendations(
    args: dict, taste_vec: np.ndarray | None, user_id: int | None
) -> tuple[str, list[dict]]:
    prefs = RecommendRequest(
        genres=args.get("genres") or [],
        mood=args.get("mood") or "",
        themes=args.get("themes") or [],
        era=args.get("era") or "any",
        length=args.get("length") or "any",
        loved_titles=args.get("loved_titles") or [],
    )
    try:
        result = await recommend_svc.recommend(prefs, taste_vec=taste_vec, user_id=user_id)
    except Exception as e:
        logger.warning(f"get_recommendations tool failed: {e}")
        return f"Recommendation lookup failed: {e}", []

    slim = [
        {
            "anilist_id": r.anilist_id,
            "title": r.title,
            "year": r.year,
            "genres": r.genres,
            "recommended_because": r.recommended_because,
        }
        for r in result.recommendations
    ]
    return json.dumps({"recommendations": slim}, ensure_ascii=False), slim


async def _agent_node(state: ChatState, taste_vec: np.ndarray | None) -> ChatState:
    client = _client()
    resp = await client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=state["messages"],
        tools=TOOLS,
        tool_choice="auto",
    )
    msg = resp.choices[0].message
    assistant_msg: dict[str, Any] = {"role": "assistant", "content": msg.content or ""}
    if msg.tool_calls:
        assistant_msg["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in msg.tool_calls
        ]
    return {
        **state,
        "messages": state["messages"] + [assistant_msg],
        "rounds": state["rounds"] + 1,
    }


async def _tools_node(
    state: ChatState, taste_vec: np.ndarray | None, user_id: int | None
) -> ChatState:
    last = state["messages"][-1]
    tool_messages: list[dict] = []
    recommendations = state["recommendations"]

    for tc in last.get("tool_calls", []):
        name = tc["function"]["name"]
        try:
            args = json.loads(tc["function"]["arguments"] or "{}")
        except json.JSONDecodeError:
            args = {}

        if name == "web_search":
            content = await _run_web_search(args.get("query", ""))
        elif name == "get_recommendations":
            content, recs = await _run_get_recommendations(args, taste_vec, user_id)
            recommendations = recs
        else:
            content = f"Unknown tool: {name}"

        tool_messages.append({"role": "tool", "tool_call_id": tc["id"], "content": content})

    return {
        **state,
        "messages": state["messages"] + tool_messages,
        "recommendations": recommendations,
    }


def _should_continue(state: ChatState) -> str:
    last = state["messages"][-1]
    if last.get("tool_calls") and state["rounds"] < MAX_TOOL_ROUNDS:
        return "tools"
    return "end"


def _build_graph(taste_vec: np.ndarray | None, user_id: int | None):
    from langgraph.graph import StateGraph

    async def agent_node(s: ChatState) -> ChatState:
        return await _agent_node(s, taste_vec)

    async def tools_node(s: ChatState) -> ChatState:
        return await _tools_node(s, taste_vec, user_id)

    graph = StateGraph(ChatState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", _should_continue, {"tools": "tools", "end": "__end__"})
    graph.add_edge("tools", "agent")
    return graph.compile()


async def run_chat(
    messages: list[dict], taste_vec: np.ndarray | None = None, user_id: int | None = None
) -> tuple[str, list[dict]]:
    """Run one turn of the conversational agent. Returns (reply_text, recommendations)."""
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    app = _build_graph(taste_vec, user_id)
    final_state: ChatState = await app.ainvoke(
        {"messages": full_messages, "recommendations": [], "rounds": 0}
    )

    reply = ""
    for m in reversed(final_state["messages"]):
        if m["role"] == "assistant" and m.get("content"):
            reply = m["content"]
            break

    return reply, final_state["recommendations"]
