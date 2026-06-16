from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load FAISS index + MongoDB connection here in later phases
    yield
    # Shutdown cleanup


app = FastAPI(title="Anime Discovery API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
