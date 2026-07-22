from pathlib import Path

# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_db"
REPORT_DIR = BASE_DIR / "reports"
TEMP_DIR = BASE_DIR / "temp"
EXPORT_DIR = BASE_DIR / "exports"

for folder in (
    UPLOAD_DIR,
    CHROMA_DIR,
    REPORT_DIR,
    TEMP_DIR,
    EXPORT_DIR
):
    folder.mkdir(parents=True, exist_ok=True)

# ==========================================================
# APPLICATION
# ==========================================================

APP_NAME = "AI Research Assistant"

PROJECT_NAME = "Multi Document Research Summarizer"

APP_VERSION = "3.0.0"

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

OLLAMA_KEEP_ALIVE = "30m"

# ==========================================================
# EMBEDDING MODEL
# ==========================================================

EMBEDDING_MODEL = "sentence-transformers/static-retrieval-mrl-en-v1"

EMBEDDING_BATCH_SIZE = 64

NORMALIZE_EMBEDDINGS = True

# ==========================================================
# PDF SETTINGS
# ==========================================================

SUPPORTED_FILE_TYPES = [
    ".pdf"
]

MAX_PDFS = 5

MAX_FILE_SIZE_MB = 50

OCR_DPI = 300

MAX_WORKERS = 4

# ==========================================================
# CHUNKING
# ==========================================================

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 150

MIN_CHUNK_LENGTH = 50

MAX_CONTEXT_CHARACTERS = 14000

# ==========================================================
# RETRIEVAL
# ==========================================================

DEFAULT_TOP_K = 10

SUMMARY_TOP_K = 35

COMPARE_TOP_K = 30

DETAIL_TOP_K = 20

CLAIM_TOP_K = 20

THEME_TOP_K = 30

CONTRADICTION_TOP_K = 30

MAX_CONTEXT_CHUNKS = 35

SEMANTIC_WEIGHT = 0.80

KEYWORD_WEIGHT = 0.20

BM25_SCORE_WEIGHT = 0.01

# ==========================================================
# LLM GENERATION
# ==========================================================

TEMPERATURE = 0.0

TOP_P = 0.80

TOP_K = 20

REPEAT_PENALTY = 1.10

MAX_TOKENS = 1024

SUMMARY_MAX_TOKENS = 800

COMPARE_MAX_TOKENS = 700

QA_MAX_TOKENS = 350

CLAIM_MAX_TOKENS = 700

THEME_MAX_TOKENS = 700

CONTRADICTION_MAX_TOKENS = 700

RESEARCH_BRIEF_MAX_TOKENS = 1000

# ==========================================================
# REPORT SETTINGS
# ==========================================================

REPORT_FILENAME = "research_brief.md"

EXPORT_MARKDOWN = True

EXPORT_JSON = False

# ==========================================================
# FEATURES
# ==========================================================

ENABLE_OCR = True

ENABLE_BM25 = True

ENABLE_CHROMA = True

ENABLE_HYBRID_SEARCH = True

ENABLE_THEME_CLUSTERING = True

ENABLE_CLAIM_EXTRACTION = True

ENABLE_CONTRADICTION_DETECTION = True

ENABLE_RESEARCH_BRIEF = True

ENABLE_MARKDOWN_EXPORT = True

# ==========================================================
# LOGGING
# ==========================================================

ENABLE_LOGGING = True

LOG_LEVEL = "INFO"