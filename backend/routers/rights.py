"""Rights router — citizen-facing legal rights information."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from backend.data.rights_scenarios import (
    get_all_scenarios, get_scenario_by_id, get_scenarios_by_category, get_categories,
)

router = APIRouter(prefix="/rights", tags=["Rights"])


@router.get("")
async def list_rights_scenarios(
    category: Optional[str] = Query(None, description="Filter by category"),
    lang: str = Query("en", description="Language for text: en, ne, hi"),
):
    """List all rights scenarios, optionally filtered by category."""
    if category:
        scenarios = get_scenarios_by_category(category)
    else:
        scenarios = get_all_scenarios()

    return {
        "scenarios": [
            {
                "id": s["id"],
                "category": s["category"],
                "title": s["title"].get(lang, s["title"]["en"]),
                "description": s["description"].get(lang, s["description"]["en"]),
            }
            for s in scenarios
        ],
        "categories": get_categories(),
    }


@router.get("/categories")
async def list_categories():
    """List available rights scenario categories."""
    return {"categories": get_categories()}


@router.get("/{scenario_id}")
async def get_rights_scenario(
    scenario_id: str,
    lang: str = Query("en", description="Language for text: en, ne, hi"),
):
    """Get a full rights scenario with all details."""
    scenario = get_scenario_by_id(scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario '{scenario_id}' not found",
        )

    def localize(obj):
        """Return the localized version of a dict field, fallback to English."""
        if isinstance(obj, dict):
            return obj.get(lang, obj.get("en", ""))
        return obj

    return {
        "id": scenario["id"],
        "category": scenario["category"],
        "title": localize(scenario["title"]),
        "description": localize(scenario["description"]),
        "your_rights": localize(scenario["your_rights"]),
        "what_authorities_must_do": localize(scenario["what_authorities_must_do"]),
        "deadlines": localize(scenario["deadlines"]),
        "where_to_go": localize(scenario["where_to_go"]),
        "provisions": scenario["provisions"],
    }
