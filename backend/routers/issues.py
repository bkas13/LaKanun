"""Issues router — Issue-to-Law Finder and plain language summaries."""

from typing import Optional

from fastapi import APIRouter, Query

from backend.services.issue_finder import find_laws_for_issue, identify_issue
from backend.data.plain_language import get_summary, get_summaries_batch
from backend.services.related import find_related_provisions
from backend.services.law import law_service

router = APIRouter(tags=["Issues & Plain Language"])


# ═══════════════════════════════════════════════════════════════════════════
# Issue-to-Law Finder (Phase 5)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/issues/identify")
async def identify_legal_issue(
    q: str = Query(..., min_length=3, description="Describe your legal issue in plain language"),
):
    """Identify what type of legal issue the user is describing."""
    issue = identify_issue(q)
    if issue:
        return {
            "identified": True,
            "issue_id": issue["id"],
            "title": issue["title"],
            "keywords": issue["keywords"],
        }
    return {"identified": False}


@router.get("/issues/find")
async def find_laws(
    q: str = Query(..., min_length=3, description="Describe your legal issue in plain language"),
    country: Optional[str] = Query(None, pattern="^(nepal|india)$"),
    lang: str = Query("en", description="Language: en, ne, hi"),
):
    """Map a legal issue description to relevant provisions and generate a brief."""
    result = find_laws_for_issue(q, country=country, lang=lang)
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Plain Language Summaries (Phase 2)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/plain-language/{article_id}")
async def get_plain_language(
    article_id: str,
    lang: str = Query("en", description="Language: en, ne, hi"),
):
    """Get a plain-language explanation of a legal provision."""
    summary = get_summary(article_id)
    if not summary:
        return {"available": False, "article_id": article_id}

    return {
        "available": True,
        "article_id": article_id,
        "summary": summary.get(lang, summary.get("en", "")),
    }


@router.get("/plain-language")
async def get_available_summaries():
    """List all articles that have plain language summaries available."""
    from backend.data.plain_language import get_all_summarized_ids
    ids = get_all_summarized_ids()
    return {"count": len(ids), "article_ids": ids}


# ═══════════════════════════════════════════════════════════════════════════
# Related Provisions (Phase 3)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/related/{article_id}")
async def get_related(
    article_id: str,
    limit: int = Query(8, ge=1, le=20),
    country: Optional[str] = Query(None, pattern="^(nepal|india)$"),
):
    """Find provisions related to a given article, filtered by country if specified."""
    article = law_service.get_by_id(article_id)
    if not article:
        return {"related": [], "article_id": article_id}

    related = find_related_provisions(article_id, article=article, limit=limit, country=country)
    return {
        "article_id": article_id,
        "article_title": article.get("title", ""),
        "article_country": article.get("country", ""),
        "related": related,
        "total": len(related),
    }
