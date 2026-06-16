export const config = {
  llmProvider: (process.env.LLM_PROVIDER ?? "openai") as
    | "openai"
    | "gemini"
    | "groq"
    | "ollama",

  openai: {
    embeddingModel: "text-embedding-3-small",
    chatModel: "gpt-4o-mini",
  },

  gemini: {
    embeddingModel: "text-embedding-004",
    chatModel: "gemini-1.5-flash",
  },

  groq: {
    // Groq has no embedding endpoint; pair with another provider for embeddings
    chatModel: "llama-3.1-8b-instant",
  },

  ollama: {
    embeddingModel: "nomic-embed-text",
    chatModel: "llama3.2",
    baseUrl: process.env.OLLAMA_BASE_URL ?? "http://localhost:11434",
  },
} as const;

export type LLMProvider = typeof config.llmProvider;
