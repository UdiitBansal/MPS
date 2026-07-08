from pathlib import Path

# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_db"
REPORT_DIR = BASE_DIR / "reports"
TEMP_DIR = BASE_DIR / "temp"

for folder in (
    UPLOAD_DIR,
    CHROMA_DIR,
    REPORT_DIR,
    TEMP_DIR
):
    folder.mkdir(parents=True, exist_ok=True)

# ==========================================================
# APPLICATION
# ==========================================================

APP_NAME = "AI Research Assistant"
PROJECT_NAME = "Multi PDF Research Summarizer"
APP_VERSION = "2.2.0"
AUTHOR = "Udiit Bansal"

# ==========================================================
# API
# ==========================================================

API_PREFIX = "/api"

ALLOWED_ORIGINS = [
    "*"
]

# ==========================================================
# OLLAMA
# ==========================================================

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_TIMEOUT = 300

# ==========================================================
# EMBEDDING MODEL
# ==========================================================

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

EMBEDDING_BATCH_SIZE = 64

NORMALIZE_EMBEDDINGS = True

# ==========================================================
# PDF SETTINGS
# ==========================================================

SUPPORTED_FILE_TYPES = [".pdf"]

MAX_PDFS = 5

MAX_FILE_SIZE_MB = 50

OCR_DPI = 200

MAX_WORKERS = 4

# ==========================================================
# CHUNKING
# ==========================================================

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 150

MAX_CONTEXT_CHARACTERS = 14000

# ==========================================================
# RETRIEVAL
# ==========================================================

DEFAULT_TOP_K = 10

SUMMARY_TOP_K = 35

COMPARE_TOP_K = 30

DETAIL_TOP_K = 20

MAX_CONTEXT_CHUNKS = 35

SEMANTIC_WEIGHT = 0.80

KEYWORD_WEIGHT = 0.20

BM25_SCORE_WEIGHT = 0.01

# ==========================================================
# GENERATION
# ==========================================================

TEMPERATURE = 0.1

TOP_P = 0.90

TOP_K = 40

REPEAT_PENALTY = 1.15

MAX_TOKENS = 1024

SUMMARY_MAX_TOKENS = 800

COMPARE_MAX_TOKENS = 700

QA_MAX_TOKENS = 350

# ==========================================================
# LOGGING
# ==========================================================

ENABLE_LOGGING = True

LOG_LEVEL = "INFO"