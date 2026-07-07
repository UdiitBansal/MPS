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
# OLLAMA
# ==========================================================

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_TIMEOUT = 300

# ==========================================================
# EMBEDDING MODEL
# ==========================================================

# Best balance of accuracy + speed for research RAG
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

EMBEDDING_BATCH_SIZE = 64
NORMALIZE_EMBEDDINGS = True

# ==========================================================
# CHUNKING
# ==========================================================

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# ==========================================================
# PDF SETTINGS
# ==========================================================

MAX_PDFS = 5

SUPPORTED_FILE_TYPES = [".pdf"]

MAX_FILE_SIZE_MB = 50

OCR_DPI = 200

# Number of worker threads used for
# parallel PDF/page processing
MAX_WORKERS = 4

# ==========================================================
# RETRIEVAL
# ==========================================================

DEFAULT_TOP_K = 10
SUMMARY_TOP_K = 35
COMPARE_TOP_K = 30
MAX_CONTEXT_CHUNKS = 35

# ==========================================================
# GENERATION
# ==========================================================

TEMPERATURE = 0.1
TOP_P = 0.9
TOP_K = 40
REPEAT_PENALTY = 1.15
MAX_TOKENS = 1024

# ==========================================================
# APPLICATION
# ==========================================================

APP_NAME = "AI Research Assistant"
APP_VERSION = "2.1.0"
AUTHOR = "Udiit Bansal"
PROJECT_NAME = "Multi PDF Research Summarizer"

# ==========================================================
# LOGGING
# ==========================================================

ENABLE_LOGGING = True
LOG_LEVEL = "INFO"