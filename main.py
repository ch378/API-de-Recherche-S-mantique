

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router
from functions import initialize_system


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Démarrage de l'API...")
    initialize_system()
    print("✅ API prête")
    yield
    print("🛑 Arrêt de l'API")


app = FastAPI(
    title="API de Recherche Sémantique",
    description="FastAPI + SentenceTransformers + Redis Stack + HNSW",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Bienvenue dans l'API de Recherche Sémantique",
        "documentation": "/docs",
        "endpoints": {
            "models": "GET /models/",
            "encode": "POST /encode/",
            "search": "POST /search/",
        },
    }


app.include_router(router)