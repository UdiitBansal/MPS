from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import (
    APP_NAME,
    APP_VERSION,
    PROJECT_NAME,
    AUTHOR,
    OLLAMA_MODEL
)

from backend.routes.upload import router as upload_router
from backend.routes.process import router as process_router
from backend.routes.chat import router as chat_router


app = FastAPI(

    title=APP_NAME,

    version=APP_VERSION,

    description="High-Speed Multi PDF Research Summarizer using FastAPI, ChromaDB, BM25 and Ollama.",

    contact={

        "name": AUTHOR

    }

)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

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

@app.get("/")
def home():

    return {

        "status": "running",

        "application": APP_NAME,

        "project": PROJECT_NAME,

        "version": APP_VERSION,

        "author": AUTHOR,

        "model": OLLAMA_MODEL,

        "features": [

            "Multi PDF Upload",

            "OCR Extraction",

            "Parallel PDF Processing",

            "Hybrid Retrieval",

            "Semantic Search",

            "BM25 Search",

            "Executive Summary",

            "Question Answering",

            "Research Report Generation"

        ]

    }


# ==========================================================
# HEALTH
# ==========================================================

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "backend": "online",

        "model": OLLAMA_MODEL

    }


# ==========================================================
# ABOUT
# ==========================================================

@app.get("/about")
def about():

    return {

        "project": PROJECT_NAME,

        "backend": "FastAPI",

        "vector_database": "ChromaDB",

        "retrieval": "Hybrid Retrieval",

        "embedding_model": "BAAI/bge-small-en-v1.5",

        "llm": OLLAMA_MODEL,

        "version": APP_VERSION

    }


# ==========================================================
# PING
# ==========================================================

@app.get("/ping")
def ping():

    return {

        "message": "Backend Connected Successfully"

    }