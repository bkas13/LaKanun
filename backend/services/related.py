"""Related provisions engine — finds articles related to a given provision.

Uses keyword-based cross-referencing to link articles across laws and countries.
"""

from typing import Optional
from backend.services.law import law_service, SYNONYMS


# ── Category relationships ──────────────────────────────────────────────
# Maps categories that are logically related (e.g., "arrest" links to "criminal_procedure")

RELATED_CATEGORIES = {
    "fundamental_rights": ["constitutional", "human_rights"],
    "constitutional": ["fundamental_rights", "federalism", "legislature", "judiciary"],
    "criminal": ["criminal_procedure_general", "punishment_provisions", "arrest_and_bail"],
    "criminal_procedure_general": ["criminal", "arrest_and_bail", "trial_proceedings"],
    "arrest_and_bail": ["criminal", "criminal_procedure_general"],
    "civil": ["civil_procedure_general", "civil_law_general", "contracts_and_obligations"],
    "civil_procedure_general": ["civil", "civil_suits"],
    "property_law": ["transfer_of_property_general", "mortgages", "leases"],
    "marriage_and_family": ["child_protection", "adoption_and_guardianship"],
    "labor_general": ["wages_and_payment", "occupational_safety"],
    "consumer_protection_general": ["consumer_courts", "consumer_complaints", "rights_of_buyer"],
    "child_protection": ["marriage_and_family", "juvenile_justice_general"],
    "cyber_crime": ["information_technology_general", "computer_offences", "data_protection"],
}

# ── Keyword groups ──────────────────────────────────────────────────────
# Words that tend to appear in related articles across different laws

KEYWORD_GROUPS = {
    "arrest": ["custody", "detention", "police", "bail", "warrant", "magistrate", "imprisonment"],
    "bail": ["bond", "surety", "release", "custody", "arrested", "detention"],
    "murder": ["homicide", "culpable", "death", "killing", "manslaughter", "302", "192"],
    "theft": ["stealing", "stolen", "robbery", "larceny", "burglary", "379", "380"],
    "fraud": ["cheating", "forgery", "deception", "embezzlement", "420"],
    "domestic_violence": ["wife", "husband", "spouse", "abuse", "shelter", "protection_order"],
    "property": ["land", "house", "building", "immovable", "partition", "inheritance", "succession"],
    "marriage": ["divorce", "matrimonial", "spouse", "wedding", "annulment"],
    "child": ["minor", "juvenile", "infant", "custody", "guardianship", "adoption"],
    "contract": ["agreement", "obligation", "breach", "damages", "specific_performance"],
    "evidence": ["witness", "proof", "testimonial", "documentary", "exhibit", "affidavit"],
    "appeal": ["revision", "review", "petition", "challenge", "tribunal", "high_court"],
    "consumer": ["buyer", "purchaser", "deficiency", "complaint", "refund", "warranty"],
    "employment": ["worker", "employee", "labour", "wages", "salary", "termination"],
    "penalty": ["punishment", "sentence", "fine", "imprisonment", "imprisonment"],
    "court": ["tribunal", "judge", "justice", "magistrate", "district_court", "high_court"],
    "privacy": ["data_protection", "personal_data", "surveillance", " interception"],
}


def find_related_provisions(
    article_id: str,
    article: Optional[dict] = None,
    limit: int = 8,
    country: Optional[str] = None,
) -> list[dict]:
    """Find provisions related to the given article.

    Strategy:
    1. Extract keywords from the article's title and text
    2. Find articles in related categories
    3. Score by keyword overlap
    4. Return top N related articles (excluding self)
    5. If country filter is active, only return articles from that country
    """
    if article is None:
        article = law_service.get_by_id(article_id)
    if article is None:
        return []

    my_country = article.get("country", "")
    my_category = article.get("category", "")
    my_id = article.get("id", "")

    # Build keyword set from this article
    title = article.get("title", "").lower()
    text = article.get("full_text", "").lower()
    combined = title + " " + text

    # Find matching keyword groups
    active_groups = set()
    for group_name, keywords in KEYWORD_GROUPS.items():
        for kw in keywords:
            if kw in combined:
                active_groups.add(group_name)
                break

    # Find related categories
    related_cats = set()
    for cat in [my_category] + list(RELATED_CATEGORIES.get(my_category, [])):
        related_cats.add(cat)
        related_cats.update(RELATED_CATEGORIES.get(cat, []))

    # Score candidate articles
    candidates = []
    for a in law_service._articles:
        if a.get("id") == my_id:
            continue

        # Country filter: if a specific country is requested, skip others
        if country and a.get("country", "") != country:
            continue

        score = 0.0
        a_text = (a.get("title", "") + " " + a.get("full_text", "")).lower()
        a_category = a.get("category", "")

        # Category match bonus
        if a_category in related_cats:
            score += 3.0

        # Cross-country bonus (same topic, different country = valuable comparison)
        if a.get("country", "") != my_country and a_category == my_category:
            score += 2.0

        # Keyword overlap scoring
        for group_name in active_groups:
            for kw in KEYWORD_GROUPS[group_name]:
                if kw in a_text:
                    score += 1.0
                    break

        # Title word overlap
        my_words = set(title.split())
        a_words = set(a.get("title", "").lower().split())
        overlap = my_words & a_words
        score += len(overlap) * 0.5

        if score >= 3.0:
            candidates.append({
                "id": a.get("id", ""),
                "title": a.get("title", ""),
                "article_number": a.get("article_number", ""),
                "country": a.get("country", ""),
                "category": a.get("category", ""),
                "source_document": a.get("source_document", ""),
                "score": score,
            })

    # Sort by score, take top N
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:limit]
