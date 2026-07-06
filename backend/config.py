from pathlib import Path

# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_db"
REPORT_DIR = BASE_DIR / "reports"
TEMP_DIR = BASE_DIR / "temp"

for folder in [

    UPLOAD_DIR,

    CHROMA_DIR,

    REPORT_DIR,

    TEMP_DIR

]:

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

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

# ==========================================================
# CHUNKING
# ==========================================================

CHUNK_SIZE = 800

CHUNK_OVERLAP = 120

# ==========================================================
# PDF SETTINGS
# ==========================================================

MAX_PDFS = 5

SUPPORTED_FILE_TYPES = [".pdf"]

MAX_FILE_SIZE_MB = 50

# ==========================================================
# RETRIEVAL
# ==========================================================

DEFAULT_TOP_K = 10

SUMMARY_TOP_K = 30

COMPARE_TOP_K = 25

MAX_CONTEXT_CHUNKS = 30

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

APP_VERSION = "2.0.0"

AUTHOR = "Udiit Bansal"

PROJECT_NAME = "Multi PDF Research Summarizer"

# ==========================================================
# LOGGING
# ==========================================================

ENABLE_LOGGING = True

LOG_LEVEL = "INFO"