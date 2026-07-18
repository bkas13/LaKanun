"""Laws router — search, browse, detail."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.dependencies import optional_user
from backend.models.user import User
from backend.schemas.law import (
    LawSearchRequest, LawSearchResponse, LawSearchResult,
    LawDetail, LawBrowseResponse,
)
from backend.services.law import law_service

router = APIRouter(prefix="/laws", tags=["Laws"])


@router.get("/search", response_model=LawSearchResponse)
async def search_laws(
    q: str = Query(..., min_length=2, max_length=1000),
    country: Optional[str] = Query(None, pattern="^(nepal|india)$"),
    category: Optional[str] = None,
    document_type: Optional[str] = None,
    sort: str = Query("relevance", pattern="^(relevance|date_newest|date_oldest|country)$"),
    top_k: int = Query(10, ge=1, le=100),
    _user: Optional[User] = Depends(optional_user),
):
    from backend.services.multilingual_search import translate_query
    lang, english_query, _ = translate_query(q)
    
    results = law_service.search(q, country=country, category=category,
                                  document_type=document_type, top_k=top_k, sort=sort)
    return LawSearchResponse(
        query=q,
        results=[
            LawSearchResult(
                id=r["article"].get("id", ""),
                title=r["article"].get("title", ""),
                full_text=r["article"].get("full_text", ""),
                country=r["article"].get("country", ""),
                category=r["article"].get("category", ""),
                document_type=r["article"].get("document_type", ""),
                article_number=r["article"].get("article_number", ""),
                source_document=r["article"].get("source_document", ""),
                score=r["score"],
                enactment_year=r["article"].get("_enactment_year", 0),
                language=r["article"].get("language", "en"),
            )
            for r in results
        ],
        total=len(results),
        detected_lang=lang,
        translated_query=english_query if lang != "en" else None,
    )


@router.get("/browse", response_model=LawBrowseResponse)
async def browse_laws(
    country: Optional[str] = Query(None, pattern="^(nepal|india)$"),
    document_type: Optional[str] = None,
    category: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _user: Optional[User] = Depends(optional_user),
):
    articles, total = law_service.browse(
        country=country, document_type=document_type,
        category=category, offset=offset, limit=limit,
    )
    return LawBrowseResponse(
        articles=[LawDetail(**a) for a in articles],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/stats")
async def law_stats(
    _user: Optional[User] = Depends(optional_user),
):
    """Public corpus statistics — no auth required."""
    from backend.services.law import law_service as svc
    _, total = svc.browse(limit=1)

    _, total_nepal = svc.browse(country="nepal", limit=1)
    _, total_india = svc.browse(country="india", limit=1)

    all_articles, _ = svc.browse(limit=10000)
    categories = {}
    for a in all_articles:
        cat = a.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1
    top_categories = sorted(categories.items(), key=lambda x: -x[1])[:8]

    return {
        "total_provisions": total,
        "nepal": total_nepal,
        "india": total_india,
        "top_categories": [{"name": k, "count": v} for k, v in top_categories],
    }


@router.get("/stats/detailed")
async def law_stats_detailed(
    _user: Optional[User] = Depends(optional_user),
):
    """Detailed corpus statistics — per-country category breakdown."""
    from backend.services.law import law_service as svc

    all_articles, _ = svc.browse(limit=10000)
    nepal_articles = [a for a in all_articles if a.get("country") == "nepal"]
    india_articles = [a for a in all_articles if a.get("country") == "india"]

    def count_by_category(arts):
        cats = {}
        for a in arts:
            cat = a.get("category", "other")
            cats[cat] = cats.get(cat, 0) + 1
        return sorted(cats.items(), key=lambda x: -x[1])

    nepal_cats = count_by_category(nepal_articles)
    india_cats = count_by_category(india_articles)

    nepal_docs = {}
    for a in nepal_articles:
        doc = a.get("source_document", "Unknown")
        nepal_docs[doc] = nepal_docs.get(doc, 0) + 1

    india_docs = {}
    for a in india_articles:
        doc = a.get("source_document", "Unknown")
        india_docs[doc] = india_docs.get(doc, 0) + 1

    return {
        "total_provisions": len(all_articles),
        "nepal": {
            "total": len(nepal_articles),
            "categories": [{"name": k, "count": v} for k, v in nepal_cats],
            "documents": [{"name": k, "count": v} for k, v in sorted(nepal_docs.items(), key=lambda x: -x[1])],
        },
        "india": {
            "total": len(india_articles),
            "categories": [{"name": k, "count": v} for k, v in india_cats],
            "documents": [{"name": k, "count": v} for k, v in sorted(india_docs.items(), key=lambda x: -x[1])],
        },
    }


@router.get("/{article_id}", response_model=LawDetail)
async def get_law_detail(
    article_id: str,
    _user: Optional[User] = Depends(optional_user),
):
    article = law_service.get_by_id(article_id)
    if not article:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provision not found")
    return LawDetail(**article)
