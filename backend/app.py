from contextlib import asynccontextmanager

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
# APPLICATION LIFECYCLE
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("\n======================================")

    print(f"{APP_NAME}")

    print(f"Version : {APP_VERSION}")

    print(f"Model   : {OLLAMA_MODEL}")

    print(f"Embedding Model : {EMBEDDING_MODEL}")

    print("Backend Started Successfully")

    print("======================================\n")

    yield

    print("\nBackend Shutdown Successfully\n")


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

@app.get("/")
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

            "/about"

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

        "model": OLLAMA_MODEL,

        "embedding_model": EMBEDDING_MODEL

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

        "embedding_model": EMBEDDING_MODEL,

        "llm": OLLAMA_MODEL,

        "version": APP_VERSION,

        "author": AUTHOR

    }

# ==========================================================
# PING
# ==========================================================

@app.get("/ping")
def ping():

    return {

        "message": "Backend Connected Successfully",

        "status": "OK"

    }