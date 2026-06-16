from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.index import load_index
from app.routers import auth, health, list, recommend


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        index, meta = load_index()
        print(f"FAISS index loaded: {index.ntotal} anime, dim={index.d}")
    except FileNotFoundError as e:
        print(f"WARNING: {e}")
    yield


app = FastAPI(title="Anime Discovery API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(recommend.router)
app.include_router(auth.router)
app.include_router(list.router)
