from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.retriever import Retriever
from backend.services.ollama_service import OllamaService
from backend.services.claim_extractor import ClaimExtractor
from backend.services.theme_extractor import ThemeExtractor
from backend.services.contradiction_detector import ContradictionDetector
from backend.services.research_brief import ResearchBriefGenerator
from backend.services.export_report import ReportExporter


# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

# =====================================================
# SERVICES
# =====================================================

retriever = Retriever()

ollama = OllamaService()

claim_extractor = ClaimExtractor()

theme_extractor = ThemeExtractor(
    retriever.hybrid.embedder
)

contradiction_detector = ContradictionDetector(
    retriever.hybrid.embedder
)

research_brief = ResearchBriefGenerator()

report_exporter = ReportExporter()

# =====================================================
# REQUEST MODEL
# =====================================================

class ChatRequest(BaseModel):

    question: str


# =====================================================
# QUERY KEYWORDS
# =====================================================

SUMMARY_KEYWORDS = {

    "summary",
    "summarize",
    "summarise",
    "overall summary",
    "executive summary",
    "research report",
    "all pdf",
    "all pdfs",
    "all documents"

}

COMPARE_KEYWORDS = {

    "compare",
    "comparison",
    "difference",
    "differences",
    "similarity",
    "similarities",
    "contrast",
    "common"

}

CLAIM_KEYWORDS = {

    "claim",
    "claims",
    "key claim",
    "key claims",
    "main claim",
    "important claim"

}

THEME_KEYWORDS = {

    "theme",
    "themes",
    "topic",
    "topics",
    "cluster",
    "clustering"

}

CONTRADICTION_KEYWORDS = {

    "contradiction",
    "contradict",
    "conflict",
    "opposite",
    "disagree"

}

REPORT_KEYWORDS = {

    "research brief",
    "brief",
    "full report",
    "complete report"

}


# =====================================================
# DETECT QUERY TYPE
# =====================================================

def detect_query_type(question: str):

    q = question.lower()

    if any(k in q for k in REPORT_KEYWORDS):
        return "report"

    if any(k in q for k in SUMMARY_KEYWORDS):
        return "summary"

    if any(k in q for k in COMPARE_KEYWORDS):
        return "comparison"

    if any(k in q for k in CLAIM_KEYWORDS):
        return "claims"

    if any(k in q for k in THEME_KEYWORDS):
        return "themes"

    if any(k in q for k in CONTRADICTION_KEYWORDS):
        return "contradictions"

    return "question"


# =====================================================
# CONTEXT SIZE
# =====================================================

def determine_chunk_limit(question):

    query_type = detect_query_type(question)

    if query_type == "summary":
        return 20

    if query_type == "comparison":
        return 15

    if query_type == "claims":
        return 15

    if query_type == "themes":
        return 20

    if query_type == "contradictions":
        return 20

    if query_type == "report":
        return 25

    return 8


# =====================================================
# BUILD CONTEXT
# =====================================================

def build_context(retrieved_chunks, max_chunks):

    context_parts = []

    sources = []

    documents = []

    seen = set()

    document_counter = {}

    MAX_CHUNKS_PER_DOCUMENT = 6

    for item in retrieved_chunks:

        if len(context_parts) >= max_chunks:

            break

        if not isinstance(item, dict):

            item = {

                "source": "Unknown",

                "page": "-",

                "chunk": "-",

                "score": 0,

                "text": str(item)

            }

        text = item.get("text", "").strip()

        if not text:

            continue

        duplicate_key = " ".join(text.split()).lower()

        if duplicate_key in seen:

            continue

        source = item.get("source", "Unknown")

        document_counter[source] = document_counter.get(source, 0) + 1

        if document_counter[source] > MAX_CHUNKS_PER_DOCUMENT:

            continue

        seen.add(duplicate_key)

        context_parts.append(

            f"""
====================================================
PDF : {source}
Page : {item.get("page","-")}
Chunk : {item.get("chunk","-")}
====================================================

{text}
"""

        )

        documents.append(

            {

                "source": source,

                "page": item.get("page", "-"),

                "chunk": item.get("chunk", "-"),

                "score": round(float(item.get("score", 0)), 4),

                "text": text

            }

        )

        sources.append(

            {

                "source": source,

                "page": item.get("page", "-"),

                "chunk": item.get("chunk", "-"),

                "score": round(float(item.get("score", 0)), 4),

                "preview": (

                    text[:300] + "..."

                    if len(text) > 300

                    else text

                )

            }

        )

    return (

        "\n".join(context_parts),

        sources,

        documents

    )
# =====================================================
# CHAT
# =====================================================

@router.post("/")
def chat(request: ChatRequest):

    start_time = datetime.now()

    question = request.question.strip()

    if not question:

        return {

            "status": "error",

            "question": "",

            "answer": "Please enter a question.",

            "sources": [],

            "retrieved_chunks": 0,

            "total_sources": 0

        }

    # -------------------------------------------------
    # Retrieve Chunks
    # -------------------------------------------------

    max_chunks = determine_chunk_limit(question)

    retrieved_chunks = retriever.search(question)

    if not retrieved_chunks:

        return {

            "status": "error",

            "question": question,

            "answer": "I could not find the answer in the uploaded documents.",

            "sources": [],

            "retrieved_chunks": 0,

            "total_sources": 0

        }

    context, sources, documents = build_context(

        retrieved_chunks,

        max_chunks

    )
    


    query_type = detect_query_type(question)

    answer = ""

    claims = None

    themes = None

    contradictions = None

    brief = None

    exports = None

    # -------------------------------------------------
    # QUESTION / SUMMARY / COMPARISON
    # -------------------------------------------------

    if query_type in (

        "question",

        "summary",

        "comparison"

    ):

        answer = ollama.generate(

            question,

            context

        )

    # -------------------------------------------------
    # CLAIMS
    # -------------------------------------------------

    elif query_type == "claims":

        claims = claim_extractor.extract(

            documents

        )

        answer = claim_extractor.to_markdown(

            claims

        )

    # -------------------------------------------------
    # THEMES
    # -------------------------------------------------

    elif query_type == "themes":

        themes = theme_extractor.extract(

            documents

        )

        answer = theme_extractor.to_markdown(

            themes

        )

    # -------------------------------------------------
    # CONTRADICTIONS
    # -------------------------------------------------

    elif query_type == "contradictions":

        contradictions = contradiction_detector.detect(

            documents

        )

        answer = contradiction_detector.to_markdown(

            contradictions

        )

    # -------------------------------------------------
    # RESEARCH BRIEF
    # -------------------------------------------------

    elif query_type == "report":

        summary = ollama.generate(

            "Generate Executive Summary",

            context

        )

        claims = claim_extractor.extract(

            documents

        )

        themes = theme_extractor.extract(

            documents

        )

        contradictions = contradiction_detector.detect(

            documents

        )

        brief = research_brief.generate(

            summaries=summary,

            claims=claims,

            themes=themes,

            contradictions=contradictions

        )

        answer = brief

        exports = report_exporter.export(

            brief

        )

    else:

        answer = ollama.generate(

            question,

            context

        )

    processing_time = round(

        (

            datetime.now()

            -

            start_time

        ).total_seconds(),

        2

    )

    unique_documents = sorted(

        {

            doc["source"]

            for doc in documents

        }

    )

    response = {

        "status": "success",

        "query_type": query_type,

        "question": question,

        "answer": answer,

        "sources": sources,

        "retrieved_chunks": len(documents),

        "total_sources": len(sources),

        "documents_used": unique_documents,

        "documents_count": len(unique_documents),

        "processing_time": processing_time,

        "timestamp": datetime.now().strftime(

            "%Y-%m-%d %H:%M:%S"

        )

    }

    # -------------------------------------------------
    # Extra AI Features
    # -------------------------------------------------

    if claims is not None:

        response["claims"] = claims

    if themes is not None:

        response["themes"] = themes

    if contradictions is not None:

        response["contradictions"] = contradictions

    if brief is not None:

        response["research_brief"] = brief

    if exports is not None:

        response["exports"] = exports

    return response


# =====================================================
# HEALTH
# =====================================================

@router.get("/health")
def health():

    return {

        "status": "healthy",

        "retriever": "Hybrid Retrieval",

        "llm": "Ollama",

        "services": {

            "question_answering": True,

            "summary": True,

            "comparison": True,

            "claims": True,

            "themes": True,

            "contradictions": True,

            "research_brief": True,

            "markdown_export": True

        }

    }


# =====================================================
# INFO
# =====================================================

@router.get("/info")
def info():

    return {

        "project": "Multi Document Research Summarizer",

        "version": "3.0",

        "retrieval": "Hybrid Retrieval",

        "vector_database": "ChromaDB",

        "keyword_search": "BM25",

        "embedding": "SentenceTransformer",

        "llm": "Ollama",

        "features": [

            "Multi PDF Upload",

            "OCR Extraction",

            "Hybrid Retrieval",

            "Question Answering",

            "Executive Summary",

            "Document Comparison",

            "Key Claim Extraction",

            "Theme Clustering",

            "Contradiction Detection",

            "Research Brief Generation",

            "Markdown Export",

            "HTML Export",

            "Source Attribution",

            "Confidence Scores"

        ]

    }
