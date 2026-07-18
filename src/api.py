"""FastAPI REST API for the legal classifier."""

import logging
import time
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.config import settings
from src.classifier import LegalClassifier, LegalAnalysis, ApplicableLaw
from src.embeddings import EmbeddingManager, SearchResult
from src.legal_dictionary import LegalDictionary

logger = logging.getLogger(__name__)

# Global instances
classifier: Optional[LegalClassifier] = None
embedding_manager: Optional[EmbeddingManager] = None
legal_dictionary: Optional[LegalDictionary] = None

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global classifier, embedding_manager, legal_dictionary

    logger.info("Starting up Nepal Legal AI API...")

    # Initialize components
    embedding_manager = EmbeddingManager()
    classifier = LegalClassifier(embedding_manager=embedding_manager)
    legal_dictionary = LegalDictionary()

    logger.info("API startup complete")
    yield

    logger.info("Shutting down...")


app = FastAPI(
    title="Nepal Legal AI API",
    description="Multilingual legal analysis API for Nepal and India",
    version="0.1.0",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request for legal analysis."""

    query: str = Field(..., min_length=10, max_length=5000, description="Legal scenario or question")
    country: str = Field(default="nepal", pattern="^(nepal|india)$")
    language: str = Field(default="en", pattern="^(en|ne|hi)$")
    top_k: int = Field(default=10, ge=1, le=50)


class AnalyzeResponse(BaseModel):
    """Response from legal analysis."""

    query_id: str
    query: str
    classification: str
    confidence: float
    applicable_laws: List[dict]
    reasoning: str
    legal_domains: List[str]
    jurisdiction: str
    severity: str
    recommended_action: str
    disclaimer: str
    timestamp: str


class ArticleResponse(BaseModel):
    """Response for article lookup."""

    id: str
    text: str
    metadata: dict


class SearchRequest(BaseModel):
    """Request for vector search."""

    q: str = Field(..., min_length=3, max_length=1000, description="Search query")
    country: Optional[str] = Field(default=None, pattern="^(nepal|india)$")
    category: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=50)


class SearchResultResponse(BaseModel):
    """Single search result."""

    id: str
    text: str
    score: float
    metadata: dict


class SearchResponse(BaseModel):
    """Search response."""

    query: str
    results: List[SearchResultResponse]
    total: int


class ArticlesListResponse(BaseModel):
    """List of articles."""

    articles: List[dict]
    total: int
    country: str
    category: str


class FeedbackRequest(BaseModel):
    """User feedback."""

    query_id: str
    rating: int = Field(..., ge=1, le=5)
    correction: Optional[str] = None
    comments: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    corpus_size: int
    countries: List[str]
    version: str


class DictionarySearchRequest(BaseModel):
    """Dictionary search request."""

    q: str = Field(..., min_length=1, max_length=100)
    lang: str = Field(default="ne", pattern="^(ne|hi)$")


# ============================================================================
# Dependency for API Key Auth (optional)
# ============================================================================

async def verify_api_key(request: Request):
    """Optional API key verification."""
    if not settings.api_keys:
        return True

    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return True


# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/analyze", response_model=AnalyzeResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("100/minute")
async def analyze_legal_scenario(request: Request, body: AnalyzeRequest):
    """Analyze a legal scenario and return classification with applicable laws."""
    start_time = time.time()

    try:
        analysis = classifier.classify(
            query=body.query,
            country=body.country,
            language=body.language,
            top_k=body.top_k,
        )

        # Convert to response model
        response = AnalyzeResponse(
            query_id=analysis.query_id,
            query=analysis.query,
            classification=analysis.classification,
            confidence=analysis.confidence,
            applicable_laws=[
                {
                    "id": law.id,
                    "country": law.country,
                    "title": law.title,
                    "text": law.text,
                    "relevance_score": law.relevance_score,
                    "stance": law.stance,
                    "explanation": law.explanation,
                    "article_number": law.article_number,
                    "category": law.category,
                }
                for law in analysis.applicable_laws
            ],
            reasoning=analysis.reasoning,
            legal_domains=analysis.legal_domains,
            jurisdiction=analysis.jurisdiction,
            severity=analysis.severity,
            recommended_action=analysis.recommended_action,
            disclaimer=analysis.disclaimer,
            timestamp=analysis.timestamp,
        )

        logger.info(f"Analysis completed in {time.time() - start_time:.2f}s")
        return response

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/article/{article_id}", response_model=ArticleResponse, dependencies=[Depends(verify_api_key)])
async def get_article(article_id: str):
    """Get full article text by ID."""
    article = embedding_manager.get_article(article_id)

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return ArticleResponse(
        id=article["id"],
        text=article["text"],
        metadata=article["metadata"],
    )


@app.get("/search", response_model=SearchResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("100/minute")
async def search_laws(
    request: Request,
    q: str,
    country: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 10,
):
    """Search legal corpus using vector similarity."""
    results = embedding_manager.search(
        query=q,
        country=country,
        category=category,
        top_k=top_k,
    )

    return SearchResponse(
        query=q,
        results=[
            SearchResultResponse(
                id=r.id,
                text=r.text,
                score=r.score,
                metadata=r.metadata,
            )
            for r in results
        ],
        total=len(results),
    )


@app.get("/articles", response_model=ArticlesListResponse, dependencies=[Depends(verify_api_key)])
async def list_articles(country: str = "nepal", category: str = "fundamental_rights"):
    """List articles filtered by country and category."""
    collection_name = f"{settings.collection_prefix}_{country}_{category}"

    if collection_name not in embedding_manager.collections:
        embedding_manager.get_or_create_collection(collection_name)

    collection = embedding_manager.collections.get(collection_name)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    try:
        result = collection.get(include=["metadatas", "documents"], limit=1000)

        articles = []
        seen = set()
        for i, meta in enumerate(result.get("metadatas", [])):
            article_id = meta.get("article_id", "")
            if article_id and article_id not in seen:
                seen.add(article_id)
                articles.append({
                    "id": article_id,
                    "title": meta.get("title", ""),
                    "country": meta.get("country", ""),
                    "category": meta.get("category", ""),
                    "article_number": meta.get("article_number", ""),
                    "language": meta.get("language", "en"),
                })

        return ArticlesListResponse(
            articles=articles,
            total=len(articles),
            country=country,
            category=category,
        )
    except Exception as e:
        logger.error(f"Failed to list articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    stats = embedding_manager.get_stats() if embedding_manager else {"total_documents": 0}

    return HealthResponse(
        status="ok",
        corpus_size=stats.get("total_documents", 0),
        countries=settings.supported_countries,
        version="0.1.0",
    )


@app.post("/feedback", dependencies=[Depends(verify_api_key)])
@limiter.limit("50/minute")
async def submit_feedback(request: Request, body: FeedbackRequest):
    """Submit user feedback for a query."""
    # In production, save to database
    logger.info(f"Feedback received: {body.query_id} - Rating: {body.rating}")

    return {
        "status": "received",
        "query_id": body.query_id,
        "message": "Thank you for your feedback!",
    }


@app.get("/dictionary/search", dependencies=[Depends(verify_api_key)])
async def search_dictionary(q: str, lang: str = "ne"):
    """Search legal dictionary for term translations."""
    results = legal_dictionary.search(q, lang)
    return {"query": q, "language": lang, "results": results}


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run the API server."""
    import uvicorn

    uvicorn.run(
        "src.api:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=True,
    )


if __name__ == "__main__":
    main()