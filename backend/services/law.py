"""Law search service — keyword search with synonym expansion + multilingual support."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from backend.config import settings
from backend.services.multilingual_search import translate_query, detect_script, DEVANAGARI_TO_ENGLISH, ROMANIZED_MAP

# ── Stop words ─────────────────────────────────────────────────────────

STOP_WORDS = frozenset([
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "to", "of", "in",
    "for", "on", "with", "at", "by", "from", "as", "into", "through",
    "during", "before", "after", "above", "below", "between", "out",
    "off", "over", "under", "again", "then", "once", "here", "there",
    "when", "where", "why", "how", "all", "each", "every", "both",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "just",
    "because", "but", "and", "or", "if", "while", "about", "against",
    "it", "its", "this", "that", "these", "those", "i", "me", "my",
    "we", "our", "you", "your", "he", "him", "his", "she", "her",
    "they", "them", "their", "what", "which", "who", "whom",
])

# ── Synonyms ───────────────────────────────────────────────────────────

SYNONYMS: Dict[str, List[str]] = {
    "theft": ["stealing", "stolen", "robbery", "larceny", "burglary", "shoplifting"],
    "murder": ["homicide", "killing", "death", "manslaughter", "culpable"],
    "cheque": ["check", "bounced", "bouncing", "dishonour", "insufficient"],
    "domestic": ["wife", "husband", "spouse", "partner", "family", "marital", "abuse"],
    "child": ["minor", "juvenile", "children", "infant", "adolescent"],
    "cyber": ["online", "internet", "digital", "computer", "hack", "hacking", "phishing"],
    "fraud": ["scam", "cheat", "deception", "forgery", "embezzlement", "defraud"],
    "bail": ["bond", "release", "surety", "custody", "arrested"],
    "marriage": ["wedding", "matrimonial", "divorce", "spouse"],
    "property": ["land", "house", "building", "immovable", "premises"],
    "employment": ["worker", "employee", "labour", "labor", "job", "wages", "salary"],
    "accident": ["collision", "crash", "injury", "motor", "vehicle", "road"],
    "evidence": ["proof", "testimonial", "documentary", "witness", "exhibit"],
    "contract": ["agreement", "deal", "pact", "covenant", "promise", "obligation"],
    "consumer": ["buyer", "purchaser", "customer", "deficiency", "complaint"],
    "penalty": ["punishment", "sentence", "fine", "imprisonment", "jail"],
    "court": ["tribunal", "judge", "justice", "bench", "judiciary", "magistrate"],
    "appeal": ["revision", "review", "petition", "challenge", "litigation"],
}

# ── Enactment Year Map ─────────────────────────────────────────────────

ENACTMENT_YEARS: Dict[str, int] = {
    # Nepal
    "constitution_of_nepal_2072": 2072,
    "nepal_penal_code": 2074,
    "nepal_criminal_procedure": 2074,
    "nepal_civil_code": 2074,
    "nepal_civil_procedure": 2074,
    "nepal_labor_act": 2074,
    "nepal_domestic_violence": 2066,
    "nepal_narcotic_drugs": 2076,
    "nepal_right_to_information": 2064,
    "nepal_electronic_transactions": 2063,
    # India
    "constitution_of_india": 1950,
    "indian_penal_code": 1860,
    "code_of_criminal_procedure": 1973,
    "code_of_civil_procedure": 1908,
    "indian_contract_act": 1872,
    "indian_evidence_act": 1872,
    "india_specific_reliefs": 1963,
    "india_transfer_of_property": 1882,
    "india_consumer_protection": 2019,
    "india_motor_vehicles": 1988,
    "india_domestic_violence": 2005,
    "india_information_technology": 2000,
    "india_negotiable_instruments": 1881,
    "india_juvenile_justice": 2015,
    "india_right_to_information": 2005,
    "india_partnership": 1932,
    "india_sale_of_goods": 1930,
    "minimum_wages_act": 1948,
}


class LawService:
    """Search and browse the legal corpus loaded from JSON files."""

    def __init__(self):
        self._articles: List[dict] = []
        self._loaded = False

    def _ensure_loaded(self):
        if self._loaded:
            return

        for filename in [
            "nepal_constitution.json", "india_constitution.json",
            "nepal_penal_code.json", "nepal_criminal_procedure.json",
            "nepal_civil_code.json", "nepal_civil_procedure.json", "nepal_labor_act.json",
            "nepal_domestic_violence.json", "nepal_narcotic_drugs.json",
            "nepal_right_to_information.json", "nepal_electronic_transactions.json",
            "india_laws.json", "india_evidence_act.json", "india_specific_reliefs.json",
            "india_transfer_of_property.json", "india_consumer_protection.json",
            "india_motor_vehicles.json", "india_domestic_violence.json",
            "india_information_technology.json", "india_negotiable_instruments.json",
            "india_juvenile_justice.json", "india_right_to_information.json",
            "india_partnership.json", "india_sale_of_goods.json",
            "minimum_wages_act.json",
        ]:
            path = settings.processed_data_dir / filename
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                    articles = data.get("articles", [])
                    # Map filename to source document key
                    file_to_doc = filename.replace(".json", "")
                    for a in articles:
                        src = a.get("source_document") or file_to_doc
                        a["source_document"] = src
                        meta = a.get("metadata", {})
                        if isinstance(meta, dict) and "constitution_year" in meta:
                            a["_enactment_year"] = meta["constitution_year"]
                        elif src in ENACTMENT_YEARS:
                            a["_enactment_year"] = ENACTMENT_YEARS[src]
                        else:
                            a["_enactment_year"] = 0
                    self._articles.extend(articles)

        self._loaded = True

    def search(
        self,
        query: str,
        country: Optional[str] = None,
        category: Optional[str] = None,
        document_type: Optional[str] = None,
        top_k: int = 10,
        sort: str = "relevance",
    ) -> List[dict]:
        self._ensure_loaded()

        # Detect language and translate query
        lang, english_query, multilingual_terms = translate_query(query)
        
        # Build expanded search terms
        q = english_query.lower().strip()
        expanded = self._expand_query(q)
        
        # Add multilingual terms directly (they're already English translations)
        for term in multilingual_terms:
            if len(term) >= 3:
                expanded.add(term.lower())
        
        # Also search with original query (in case it has English parts)
        original_q = query.lower().strip()
        
        results = []

        for a in self._articles:
            if country and a.get("country") != country:
                continue
            if category and a.get("category") != category:
                continue
            if document_type and a.get("document_type") != document_type:
                continue

            text = (a.get("full_text", "") + " " + a.get("title", "")).lower()
            title_lower = a.get("title", "").lower()
            score = 0

            # Score against original query (handles English or mixed)
            if original_q in text:
                score += 15
            if original_q in title_lower:
                score += 12

            # Score against translated English query
            if q != original_q and q in text:
                score += 15
            if q != original_q and q in title_lower:
                score += 12

            # Score each expanded term
            for term in expanded:
                if len(term) < 3:
                    continue
                score += self._fuzzy_score(text, term) * 0.8
                score += self._fuzzy_score(title_lower, term)

            # Bonus: if any multilingual term matches, boost score
            for term in multilingual_terms:
                if term.lower() in text:
                    score += 8

            if score > 0:
                results.append({"article": a, "score": score})

        # Sort
        if sort == "date_newest":
            results.sort(key=lambda x: x["article"].get("_enactment_year", 0), reverse=True)
        elif sort == "date_oldest":
            results.sort(key=lambda x: x["article"].get("_enactment_year", 0))
        elif sort == "country":
            results.sort(key=lambda x: (
                x["article"].get("country", ""),
                -x["score"]
            ))
        else:
            results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]

    def browse(
        self,
        country: Optional[str] = None,
        document_type: Optional[str] = None,
        category: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[List[dict], int]:
        self._ensure_loaded()

        filtered = self._articles
        if country:
            filtered = [a for a in filtered if a.get("country") == country]
        if document_type:
            filtered = [a for a in filtered if a.get("document_type") == document_type]
        if category:
            filtered = [a for a in filtered if a.get("category") == category]

        total = len(filtered)
        return filtered[offset: offset + limit], total

    def get_by_id(self, article_id: str) -> Optional[dict]:
        self._ensure_loaded()
        for a in self._articles:
            if a.get("id") == article_id:
                return a
        return None

    @staticmethod
    def _expand_query(q: str) -> set:
        words = q.lower().split()
        words = [w for w in words if len(w) > 3 and w not in STOP_WORDS]
        expanded = set(words)
        for w in words:
            for syn_key, syn_list in SYNONYMS.items():
                group = [syn_key] + syn_list
                if any(g in w or w in g for g in group):
                    expanded.update(group)
        return expanded

    @staticmethod
    def _fuzzy_score(text: str, term: str) -> float:
        idx = text.find(term)
        if idx == -1:
            return 0
        score = 5.0
        if idx == 0:
            score += 3
        before = text[idx - 1] if idx > 0 else " "
        if before in (" ", "\n"):
            score += 2
        return score


# Singleton
law_service = LawService()
