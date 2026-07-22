from datetime import datetime
import logging
from collections import defaultdict

from fastapi import APIRouter
from pydantic import BaseModel

from backend.indexes.document_index import index

from backend.services.retriever import Retriever
from backend.services.ollama_service import OllamaService
from backend.services.claim_extractor import ClaimExtractor
from backend.services.theme_extractor import ThemeExtractor
from backend.services.contradiction_detector import ContradictionDetector
from backend.services.research_brief import ResearchBriefGenerator
from backend.services.export_report import ReportExporter


# ==========================================================
# LOGGING
# ==========================================================

logger = logging.getLogger(__name__)


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# ==========================================================
# SERVICES
# ==========================================================

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


# ==========================================================
# REQUEST MODEL
# ==========================================================

class ChatRequest(BaseModel):
    question: str


# ==========================================================
# QUERY KEYWORDS
# ==========================================================

SUMMARY_KEYWORDS = {
    "summary",
    "summarize",
    "summarise",
    "overall summary",
    "executive summary",
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
    "main claim",
    "key claim",
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


# ==========================================================
# GREETINGS
# ==========================================================

GREETINGS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening"
}

THANKS = {
    "thanks",
    "thank you"
}

GOODBYE = {
    "bye",
    "goodbye"
}


# ==========================================================
# QUERY DETECTOR
# ==========================================================

def detect_query_type(question: str) -> str:

    q = question.lower().strip()

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


# ==========================================================
# CHUNK LIMIT
# ==========================================================

def determine_chunk_limit(query_type: str) -> int:

    limits = {
        "question": 8,
        "summary": 20,
        "comparison": 15,
        "claims": 15,
        "themes": 20,
        "contradictions": 20,
        "report": 25
    }

    return limits.get(query_type, 8)


# ==========================================================
# GROUP CHUNKS BY DOCUMENT
# ==========================================================

def group_chunks_by_document(chunks):

    grouped = defaultdict(list)

    for chunk in chunks:

        grouped[
            chunk.get("source", "Unknown")
        ].append(chunk)

    return grouped


# ==========================================================
# BUILD CONTEXT
# ==========================================================

def build_context(retrieved_chunks, max_chunks):

    context = []

    documents = []

    sources = []

    seen = set()

    grouped = group_chunks_by_document(retrieved_chunks)

    MAX_CHUNKS_PER_DOCUMENT = 3

    total = 0

    for source, chunks in grouped.items():

        chunks = sorted(
            chunks,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        for chunk in chunks[:MAX_CHUNKS_PER_DOCUMENT]:

            if total >= max_chunks:
                break

            text = chunk.get("text", "").strip()

            if not text:
                continue

            duplicate = " ".join(
                text.split()
            ).lower()

            if duplicate in seen:
                continue

            seen.add(duplicate)

            context.append(
                f"""
====================================================
PDF : {source}
Page : {chunk.get('page','-')}
Chunk : {chunk.get('chunk','-')}
====================================================

{text}
"""
            )

            documents.append(
                {
                    "source": source,
                    "page": chunk.get("page", "-"),
                    "chunk": chunk.get("chunk", "-"),
                    "score": round(
                        float(chunk.get("score", 0)),
                        4
                    ),
                    "text": text
                }
            )

            sources.append(
                {
                    "source": source,
                    "page": chunk.get("page", "-"),
                    "chunk": chunk.get("chunk", "-"),
                    "score": round(
                        float(chunk.get("score", 0)),
                        4
                    ),
                    "preview": (
                        text[:300] + "..."
                        if len(text) > 300
                        else text
                    )
                }
            )

            total += 1

    logger.info(
        "Retriever -> %d chunks from %d documents",
        len(documents),
        len(grouped)
    )

    return (
        "\n".join(context),
        sources,
        documents
    )
@router.post("/")
def chat(request: ChatRequest):

    start_time = datetime.now()

    try:

        # =====================================================
        # VALIDATE QUESTION
        # =====================================================

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

        query_type = detect_query_type(question)

        logger.info("=" * 70)
        logger.info("New Question")
        logger.info("Question    : %s", question)
        logger.info("Query Type  : %s", query_type)

        # =====================================================
        # SIMPLE CONVERSATION
        # =====================================================

        q = question.lower()

        if q in GREETINGS:

            if index.is_ready():

                return {
                    "status": "success",
                    "query_type": "greeting",
                    "question": question,
                    "answer": (
                        "👋 Hello!\n\n"
                        "Your documents are ready.\n\n"
                        "You can now:\n"
                        "• Ask questions\n"
                        "• Generate executive summaries\n"
                        "• Compare documents\n"
                        "• Extract key claims\n"
                        "• Find common themes\n"
                        "• Detect contradictions\n"
                        "• Generate research reports"
                    ),
                    "sources": [],
                    "retrieved_chunks": 0,
                    "total_sources": 0
                }

            return {
                "status": "success",
                "query_type": "greeting",
                "question": question,
                "answer": (
                    "👋 Hello!\n\n"
                    "Please upload and process one or more PDF documents first."
                ),
                "sources": [],
                "retrieved_chunks": 0,
                "total_sources": 0
            }

        if q in THANKS:

            return {
                "status": "success",
                "query_type": "thanks",
                "question": question,
                "answer": "😊 You're welcome! Happy to help.",
                "sources": [],
                "retrieved_chunks": 0,
                "total_sources": 0
            }

        if q in GOODBYE:

            return {
                "status": "success",
                "query_type": "goodbye",
                "question": question,
                "answer": (
                    "👋 Goodbye!\n\n"
                    "Thanks for using the AI Research Assistant."
                ),
                "sources": [],
                "retrieved_chunks": 0,
                "total_sources": 0
            }

        # =====================================================
        # DOCUMENT CHECK
        # =====================================================

        if not index.is_ready():

            logger.warning("Document index is not ready.")

            return {
                "status": "error",
                "question": question,
                "answer": (
                    "Please upload and process one or more PDF documents "
                    "before asking questions."
                ),
                "sources": [],
                "retrieved_chunks": 0,
                "total_sources": 0
            }

        # =====================================================
        # RETRIEVE DOCUMENTS
        # =====================================================

        max_chunks = determine_chunk_limit(query_type)

        retrieved_chunks = retriever.search(question)

        if not retrieved_chunks:

            logger.warning("Retriever returned no results.")

            return {
                "status": "error",
                "question": question,
                "answer": (
                    "I couldn't find relevant information in the uploaded "
                    "documents for your question."
                ),
                "sources": [],
                "retrieved_chunks": 0,
                "total_sources": 0
            }

        context, sources, documents = build_context(
            retrieved_chunks,
            max_chunks
        )

        if not context.strip():

            logger.warning("Context generation failed.")

            return {
                "status": "error",
                "question": question,
                "answer": (
                    "The retrieved documents contained no usable text."
                ),
                "sources": [],
                "retrieved_chunks": 0,
                "total_sources": 0
            }

        logger.info("Retrieved Chunks : %d", len(documents))
        logger.info("Unique Documents : %d",
                    len({d['source'] for d in documents}))
        logger.info("Context Length   : %d", len(context))

        # =====================================================
        # VARIABLES
        # =====================================================

        answer = ""

        claims = None

        themes = None

        contradictions = None

        brief = None

        exports = None

        summary = None

        unique_documents = sorted(
            {
                doc["source"]
                for doc in documents
            }
        )

        # =====================================================
        # AI PROCESSING STARTS HERE
        # =====================================================
                # =====================================================
        # QUESTION / SUMMARY / COMPARISON
        # =====================================================

        if query_type in ("question", "summary", "comparison"):

            answer = ollama.generate(
                question=question,
                context=context
            )

        # =====================================================
        # CLAIM EXTRACTION
        # =====================================================

        elif query_type == "claims":

            claims = claim_extractor.extract(documents)

            answer = claim_extractor.to_markdown(claims)

        # =====================================================
        # THEME EXTRACTION
        # =====================================================

        elif query_type == "themes":

            themes = theme_extractor.extract(documents)

            answer = theme_extractor.to_markdown(themes)

        # =====================================================
        # CONTRADICTION DETECTION
        # =====================================================

        elif query_type == "contradictions":

            contradictions = contradiction_detector.detect(
                documents
            )

            answer = contradiction_detector.to_markdown(
                contradictions
            )

        # =====================================================
        # RESEARCH REPORT
        # =====================================================

        elif query_type == "report":

            logger.info("Generating Executive Summary...")

            summary = ollama.generate(
                question="Generate a comprehensive executive summary.",
                context=context
            )

            logger.info("Extracting Claims...")
            claims = claim_extractor.extract(documents)

            logger.info("Extracting Themes...")
            themes = theme_extractor.extract(documents)

            logger.info("Detecting Contradictions...")
            contradictions = contradiction_detector.detect(
                documents
            )

            logger.info("Generating Research Brief...")

            brief = research_brief.generate(
                summaries=summary,
                claims=claims,
                themes=themes,
                contradictions=contradictions
            )

            answer = brief

            logger.info("Exporting Report...")

            exports = report_exporter.export(brief)

        # =====================================================
        # DEFAULT
        # =====================================================

        else:

            answer = ollama.generate(
                question=question,
                context=context
            )

        # =====================================================
        # FALLBACK
        # =====================================================

        if not answer or not answer.strip():

            answer = (
                "I couldn't generate a meaningful response "
                "from the uploaded documents."
            )

        # =====================================================
        # PROCESSING TIME
        # =====================================================

        processing_time = round(
            (
                datetime.now() - start_time
            ).total_seconds(),
            2
        )

        # =====================================================
        # RESPONSE
        # =====================================================

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

        # =====================================================
        # OPTIONAL AI OUTPUTS
        # =====================================================

        if summary is not None:
            response["summary"] = summary

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

        logger.info(
            "Completed in %.2f seconds",
            processing_time
        )

        logger.info("=" * 70)

        return response

    # =====================================================
    # EXCEPTION HANDLER
    # =====================================================

    except Exception as e:

        logger.exception("Chat API Error")

        return {

            "status": "error",

            "question": request.question,

            "answer": (
                "An unexpected error occurred while "
                "processing your request."
            ),

            "error": str(e),

            "sources": [],

            "retrieved_chunks": 0,

            "total_sources": 0

        }
