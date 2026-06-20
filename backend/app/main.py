from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import FRONTEND_URL
from app.core.db import close_db
from app.core.index import load_index
from app.routers import anime, auth, chat, health, list, mal, mal_auth, recommend


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        index, meta = load_index()
        print(f"FAISS index loaded: {index.ntotal} anime, dim={index.d}")
    except FileNotFoundError as e:
        print(f"WARNING: {e}")
    yield
    close_db()


app = FastAPI(title="Anime Discovery API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(recommend.router)
app.include_router(anime.router)
app.include_router(auth.router)
app.include_router(list.router)
app.include_router(chat.router)
app.include_router(mal_auth.router)
app.include_router(mal.router)
