from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import (
    APP_NAME,
    APP_VERSION,
    PROJECT_NAME,
    AUTHOR,
    OLLAMA_MODEL,
    EMBEDDING_MODEL,
    ALLOWED_ORIGINS
)

from backend.routes.upload import router as upload_router
from backend.routes.process import router as process_router
from backend.routes.chat import router as chat_router

# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ==========================================================
# APPLICATION LIFECYCLE
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("======================================")
        logger.info(APP_NAME)
        logger.info(f"Version : {APP_VERSION}")
        logger.info(f"Model   : {OLLAMA_MODEL}")
        logger.info(f"Embedding Model : {EMBEDDING_MODEL}")
        logger.info("Backend Started Successfully")
        logger.info("======================================")

        yield

    finally:
        logger.info("Backend Shutdown Successfully")

# ==========================================================
# FASTAPI
# ==========================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="High-Speed Multi PDF Research Summarizer using FastAPI, ChromaDB, BM25, EasyOCR and Ollama.",
    contact={
        "name": AUTHOR
    },
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Upload",
            "description": "Upload PDF Documents"
        },
        {
            "name": "Processing",
            "description": "Generate Embeddings & Index"
        },
        {
            "name": "Chat",
            "description": "Question Answering"
        },
        {
            "name": "System",
            "description": "Application Information"
        }
    ]
)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ==========================================================
# ROUTES
# ==========================================================

app.include_router(upload_router)
app.include_router(process_router)
app.include_router(chat_router)

# ==========================================================
# HOME
# ==========================================================

@app.get("/", tags=["System"])
def home():

    return {
        "status": "running",
        "application": APP_NAME,
        "project": PROJECT_NAME,
        "version": APP_VERSION,
        "author": AUTHOR,
        "model": OLLAMA_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "features": [
            "Multi PDF Upload",
            "OCR Extraction",
            "Parallel Processing",
            "Hybrid Retrieval",
            "Semantic Search",
            "BM25 Search",
            "Executive Summary",
            "Question Answering",
            "Research Report Generation"
        ],
        "endpoints": [
            "/upload",
            "/process",
            "/chat",
            "/health",
            "/about",
            "/ping"
        ]
    }

# ==========================================================
# HEALTH
# ==========================================================

@app.get("/health", tags=["System"])
def health():

    return {
        "status": "healthy",
        "backend": "online",
        "project": PROJECT_NAME,
        "version": APP_VERSION,
        "model": OLLAMA_MODEL,
        "embedding_model": EMBEDDING_MODEL
    }

# ==========================================================
# ABOUT
# ==========================================================

@app.get("/about", tags=["System"])
def about():

    return {
        "project": PROJECT_NAME,
        "backend": "FastAPI",
        "vector_database": "ChromaDB",
        "retrieval": "Hybrid Retrieval",
        "embedding_model": EMBEDDING_MODEL,
        "llm": OLLAMA_MODEL,
        "version": APP_VERSION,
        "author": AUTHOR
    }

# ==========================================================
# PING
# ==========================================================

@app.get("/ping", tags=["System"])
def ping():

    return {
        "message": "Backend Connected Successfully",
        "status": "OK"
    }