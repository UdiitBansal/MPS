from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import OLLAMA_MODEL
from backend.routes.upload import router as upload_router
from backend.routes.process import router as process_router
from backend.routes.chat import router as chat_router

app = FastAPI(

    title="AI Research Assistant",

    description="Multi PDF Research Summarizer using FastAPI, ChromaDB, BM25 and Ollama",

    version="2.0.0"

)

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)

app.include_router(upload_router)
app.include_router(process_router)
app.include_router(chat_router)


@app.get("/")
def home():

    return {

        "status": "running",

        "application": "AI Research Assistant",

        "version": "2.0.0",

        "model": OLLAMA_MODEL,

        "features": [

            "Multi PDF Upload",

            "Automatic Processing",

            "Hybrid Retrieval",

            "Semantic Search",

            "BM25 Search",

            "Executive Summary",

            "Question Answering"

        ]

    }


@app.get("/health")
def health():

    return {

        "status": "healthy",

        "backend": "online",

        "ollama_model": OLLAMA_MODEL

    }


@app.get("/about")
def about():

    return {

        "project": "Multi PDF Research Summarizer",

        "backend": "FastAPI",

        "vector_database": "ChromaDB",

        "retrieval": "Hybrid (Semantic + BM25)",

        "llm": OLLAMA_MODEL,

        "version": "2.0.0"

    }


@app.get("/ping")
def ping():

    return {

        "message": "Backend Connected Successfully"

    }