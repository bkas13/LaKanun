"""Laws router — search, browse, detail, popular, categories, recent."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select, func

from backend.dependencies import optional_user, require_current_user, require_lawyer
from backend.models.user import User
from backend.models.law_view import LawView
from backend.models.bookmark import Bookmark
from backend.schemas.law import (
    LawSearchRequest, LawSearchResponse, LawSearchResult,
    LawDetail, LawBrowseResponse, LawPopularResponse,
    LawCategoryResponse, LawRecentResponse,
    LawBookmarkRequest, LawBookmarkResponse,
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
                confidence=r.get("confidence", "low"),
                citation=r.get("citation", ""),
                last_verified=r["article"].get("_last_verified", ""),
                source_url=r["article"].get("_source_url", ""),
                effective_date=r["article"].get("_effective_date", ""),
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


@router.get("/popular")
async def get_popular_laws(
    country: Optional[str] = Query(None, pattern="^(nepal|india)$"),
    limit: int = Query(10, ge=1, le=50),
    _user: Optional[User] = Depends(optional_user),
):
    """Get most viewed provisions. Falls back to curated essentials when no views exist."""
    from backend.database import async_session

    # Try real view data first
    async with async_session() as session:
        query = (
            select(
                LawView.provision_id,
                func.sum(LawView.view_count).label("total_views"),
            )
            .group_by(LawView.provision_id)
        )
        if country:
            query = query.where(LawView.country == country)
        query = query.order_by(func.sum(LawView.view_count).desc()).limit(limit)
        result = await session.execute(query)
        rows = result.all()

        popular = []
        for row in rows:
            article = law_service.get_by_id(row.provision_id)
            if article:
                popular.append(LawPopularResponse(
                    provision_id=row.provision_id,
                    title=article.get("title", ""),
                    country=article.get("country", ""),
                    category=article.get("category", ""),
                    view_count=row.total_views,
                    article_number=article.get("article_number", ""),
                    source_document=article.get("source_document", ""),
                ))

    # Fallback: curated "essential provisions" when no view data exists
    if not popular:
        CURATED_IDS = [
            # Nepal essentials
            "nepal_constitution_2072_art_16",
            "nepal_constitution_2072_art_17",
            "nepal_constitution_2072_art_18",
            "nepal_constitution_2072_art_35",
            "nepal_penal_code_sec_302",
            "nepal_penal_code_sec_303",
            "nepal_civil_code_sec_11",
            "nepal_civil_code_sec_12",
            "nepal_domestic_violence_sec_3",
            "nepal_labor_act_sec_96",
            "nepal_criminal_procedure_sec_54",
            "nepal_narcotic_drugs_sec_8",
            # India essentials
            "india_constitution_art_14",
            "india_constitution_art_19",
            "india_constitution_art_21",
            "india_constitution_art_32",
            "indian_penal_code_sec_302",
            "indian_penal_code_sec_304",
            "code_of_criminal_procedure_sec_41",
            "code_of_civil_procedure_sec_9",
            "india_consumer_protection_sec_2",
            "india_domestic_violence_sec_3",
            "india_motor_vehicles_sec_134",
            "india_negotiable_instruments_sec_138",
        ]

        for cid in CURATED_IDS:
            article = law_service.get_by_id(cid)
            if article:
                if country and article.get("country") != country:
                    continue
                popular.append(LawPopularResponse(
                    provision_id=cid,
                    title=article.get("title", ""),
                    country=article.get("country", ""),
                    category=article.get("category", ""),
                    view_count=0,
                    article_number=article.get("article_number", ""),
                    source_document=article.get("source_document", ""),
                ))
                if len(popular) >= limit:
                    break

    return popular


@router.get("/categories")
async def get_law_categories(
    country: Optional[str] = Query(None, pattern="^(nepal|india)$"),
    _user: Optional[User] = Depends(optional_user),
):
    """Get all law categories with counts — public, no auth required."""
    all_articles, _ = law_service.browse(limit=10000)
    
    categories = {}
    for a in all_articles:
        cat = a.get("category", "other")
        if country and a.get("country") != country:
            continue
        if cat not in categories:
            categories[cat] = {"name": cat, "count": 0, "countries": {}}
        categories[cat]["count"] += 1
        c = a.get("country", "unknown")
        categories[cat]["countries"][c] = categories[cat]["countries"].get(c, 0) + 1
    
    return sorted(categories.values(), key=lambda x: -x["count"])


@router.get("/recent")
async def get_recent_laws(
    country: Optional[str] = Query(None, pattern="^(nepal|india)$"),
    limit: int = Query(10, ge=1, le=50),
    _user: Optional[User] = Depends(optional_user),
):
    """Get recently enacted laws — public, no auth required."""
    all_articles, _ = law_service.browse(limit=10000)
    
    recent = []
    seen = set()
    for a in all_articles:
        year = a.get("_enactment_year", 0)
        if year > 0:
            if country and a.get("country") != country:
                continue
            src = a.get("source_document", "")
            if src in seen:
                continue
            seen.add(src)
            recent.append(LawRecentResponse(
                provision_id=a.get("id", ""),
                title=a.get("title", ""),
                country=a.get("country", ""),
                category=a.get("category", ""),
                enactment_year=year,
                article_number=a.get("article_number", ""),
                source_document=src,
            ))
    
    recent.sort(key=lambda x: -x.enactment_year)
    return recent[:limit]


@router.post("/{article_id}/view")
async def track_view(
    article_id: str,
    _user: Optional[User] = Depends(optional_user),
):
    """Track a provision view — updates popularity ranking."""
    article = law_service.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provision not found")
    
    from backend.database import async_session
    async with async_session() as session:
        user_id = _user.id if _user else 0
        
        result = await session.execute(
            select(LawView).where(
                LawView.provision_id == article_id,
                LawView.user_id == user_id,
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.view_count += 1
        else:
            new_view = LawView(
                user_id=user_id,
                provision_id=article_id,
                country=article.get("country", ""),
                category=article.get("category", ""),
                view_count=1,
            )
            session.add(new_view)
        
        await session.commit()
    
    return {"status": "ok", "message": "View tracked"}


@router.post("/bookmarks", response_model=LawBookmarkResponse)
async def create_bookmark(
    request: LawBookmarkRequest,
    user: User = Depends(require_lawyer),
):
    """Create a bookmark from laws page — requires lawyer+ role."""
    from backend.database import async_session
    async with async_session() as session:
        bookmark = Bookmark(
            user_id=user.id,
            provision_id=request.provision_id,
            country=request.country,
            document_type=request.category,
            title=request.title,
            note=request.note,
        )
        session.add(bookmark)
        await session.commit()
        await session.refresh(bookmark)
        
        return LawBookmarkResponse(
            id=bookmark.id,
            provision_id=bookmark.provision_id,
            country=bookmark.country,
            title=bookmark.title or "",
            note=bookmark.note or "",
            created_at=bookmark.created_at.isoformat() if bookmark.created_at else "",
        )


@router.get("/bookmarks/check/{provision_id}")
async def check_bookmark(
    provision_id: str,
    user: User = Depends(require_lawyer),
):
    """Check if a provision is bookmarked by the current user."""
    from backend.database import async_session
    async with async_session() as session:
        result = await session.execute(
            select(Bookmark).where(
                Bookmark.user_id == user.id,
                Bookmark.provision_id == provision_id,
            )
        )
        bookmark = result.scalar_one_or_none()
        return {"bookmarked": bookmark is not None, "id": bookmark.id if bookmark else None}


@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: int,
    user: User = Depends(require_lawyer),
):
    """Delete a bookmark."""
    from backend.database import async_session
    async with async_session() as session:
        result = await session.execute(
            select(Bookmark).where(
                Bookmark.id == bookmark_id,
                Bookmark.user_id == user.id,
            )
        )
        bookmark = result.scalar_one_or_none()
        if not bookmark:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
        await session.delete(bookmark)
        await session.commit()
        return {"status": "ok", "message": "Bookmark deleted"}


@router.get("/combined-search")
async def combined_search(
    q: str = Query(..., min_length=2, max_length=1000),
    mode: str = Query("auto", pattern="^(auto|laws|issues)$"),
    country: Optional[str] = Query(None, pattern="^(nepal|india)$"),
    lang: str = Query("en", description="Language: en, ne, hi"),
    top_k: int = Query(15, ge=1, le=50),
    _user: Optional[User] = Depends(optional_user),
):
    """Combined search: mode=laws for keyword search, mode=issues for issue-to-law,
    mode=auto tries issues first then falls back to keyword search."""
    from backend.services.issue_finder import identify_issue, find_laws_for_issue
    from backend.services.multilingual_search import translate_query

    if mode == "laws":
        # Pure keyword search
        results = law_service.search(q, country=country, top_k=top_k)
        return {
            "mode_used": "laws",
            "results": [
                {
                    "id": r["article"].get("id", ""),
                    "title": r["article"].get("title", ""),
                    "full_text": r["article"].get("full_text", ""),
                    "country": r["article"].get("country", ""),
                    "category": r["article"].get("category", ""),
                    "document_type": r["article"].get("document_type", ""),
                    "article_number": r["article"].get("article_number", ""),
                    "source_document": r["article"].get("source_document", ""),
                    "score": r["score"],
                    "enactment_year": r["article"].get("_enactment_year", 0),
                    "confidence": r.get("confidence", "low"),
                    "citation": r.get("citation", ""),
                }
                for r in results
            ],
            "issue": None,
        }

    if mode == "issues":
        # Issue-to-law finder
        result = find_laws_for_issue(q, country=country, lang=lang)
        return {
            "mode_used": "issues",
            "results": result.get("search_results", []),
            "issue": {
                "identified": result.get("issue_identified", False),
                "issue_id": result.get("issue_id"),
                "title": result.get("title", ""),
                "provisions": result.get("provisions", []),
                "guidance": result.get("guidance", ""),
            },
        }

    # mode=auto: try issue identification first, fall back to keyword
    issue = identify_issue(q)
    if issue:
        result = find_laws_for_issue(q, country=country, lang=lang)
        return {
            "mode_used": "issues",
            "results": result.get("search_results", []),
            "issue": {
                "identified": True,
                "issue_id": result.get("issue_id"),
                "title": result.get("title", ""),
                "provisions": result.get("provisions", []),
                "guidance": result.get("guidance", ""),
            },
        }

    # Fallback: keyword search
    results = law_service.search(q, country=country, top_k=top_k)
    return {
        "mode_used": "laws",
        "results": [
            {
                "id": r["article"].get("id", ""),
                "title": r["article"].get("title", ""),
                "full_text": r["article"].get("full_text", ""),
                "country": r["article"].get("country", ""),
                "category": r["article"].get("category", ""),
                "document_type": r["article"].get("document_type", ""),
                "article_number": r["article"].get("article_number", ""),
                "source_document": r["article"].get("source_document", ""),
                "score": r["score"],
                "enactment_year": r["article"].get("_enactment_year", 0),
                "confidence": r.get("confidence", "low"),
                "citation": r.get("citation", ""),
            }
            for r in results
        ],
        "issue": None,
    }


@router.get("/{article_id}", response_model=LawDetail)
async def get_law_detail(
    article_id: str,
    _user: Optional[User] = Depends(optional_user),
):
    article = law_service.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provision not found")
    return LawDetail(**article)
