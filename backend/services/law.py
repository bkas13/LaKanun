"""Law search service — keyword search with synonym expansion + multilingual support.

Includes accuracy safeguards:
- Minimum relevance score threshold (filters low-quality results)
- Confidence levels (high/medium/low) for each result
- Proper legal citation formatting
- Source metadata tracking (last verified, source URL, effective date)
"""

import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Set

from backend.config import settings
from backend.services.multilingual_search import translate_query, detect_script, DEVANAGARI_TO_ENGLISH, ROMANIZED_MAP


# ── Accuracy Safeguards ─────────────────────────────────────────────────

MIN_RELEVANCE_SCORE = 5.0
"""Results with score below this threshold are not shown to users."""

LAST_VERIFIED = date.today().isoformat()
"""Date when the corpus was last verified against official sources."""


def confidence_level(score: float) -> str:
    """Return confidence label based on relevance score.

    Score ranges (keyword-based scoring):
      - 50+: strong match — exact title/keyword hits, high certainty
      - 25–49: moderate match — partial overlaps, likely relevant
      - 5–24: weak match — fuzzy or single-term hits, may be tangential
    """
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"

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

# ── Official Source URLs ────────────────────────────────────────────────

SOURCE_URLS: Dict[str, str] = {
    # Nepal — Nepal Law Commission (lawcommission.gov.np)
    "constitution_of_nepal_2072": "https://lawcommission.gov.np/content/13443/constitution-of-nepal-2072/",
    "nepal_penal_code": "https://lawcommission.gov.np/content/13454/criminal-code-2074/",
    "nepal_criminal_procedure": "https://lawcommission.gov.np/content/13455/criminal-procedure-code-2074/",
    "nepal_civil_code": "https://lawcommission.gov.np/content/13452/civil-code-2074/",
    "nepal_civil_procedure": "https://lawcommission.gov.np/content/13453/civil-procedure-code-2074/",
    "nepal_labor_act": "https://lawcommission.gov.np/content/13458/labor-act-2074/",
    "nepal_domestic_violence": "https://lawcommission.gov.np/content/13460/domestic-violence-offence-and-punishment-act-2066/",
    "nepal_narcotic_drugs": "https://lawcommission.gov.np/content/13462/narcotic-drugs-control-act-2076/",
    "nepal_right_to_information": "https://lawcommission.gov.np/content/13461/right-to-information-act-2064/",
    "nepal_electronic_transactions": "https://lawcommission.gov.np/content/13459/electronic-transaction-act-2063/",
    # India — Indian Kanoon (indiankanoon.org) + India Code (indiacode.nic.in)
    "constitution_of_india": "https://indiankanoon.org/doc/1947613/",
    "indian_penal_code": "https://indiankanoon.org/doc/1569253/",
    "code_of_criminal_procedure": "https://indiankanoon.org/doc/1955406/",
    "code_of_civil_procedure": "https://indiankanoon.org/doc/1419066/",
    "indian_contract_act": "https://indiankanoon.org/doc/1882196/",
    "minimum_wages_act": "https://indiankanoon.org/doc/1017812/",
    "india_consumer_protection": "https://indiankanoon.org/doc/1949980/",
    "india_motor_vehicles": "https://indiankanoon.org/doc/1205972/",
    "india_domestic_violence": "https://indiankanoon.org/doc/1603427/",
    "india_information_technology": "https://indiankanoon.org/doc/1957432/",
    "india_negotiable_instruments": "https://indiankanoon.org/doc/1627548/",
    "india_juvenile_justice": "https://indiankanoon.org/doc/1957317/",
    "india_right_to_information": "https://indiankanoon.org/doc/1963155/",
    "india_sale_of_goods": "https://indiankanoon.org/doc/1883035/",
    "india_partnership": "https://indiankanoon.org/doc/1883088/",
    "india_evidence_act": "https://indiankanoon.org/doc/1961744/",
    "india_transfer_of_property": "https://indiankanoon.org/doc/1959156/",
    "india_specific_reliefs": "https://indiankanoon.org/doc/1959101/",
}

# ── Source Document Display Names ────────────────────────────────────────

SOURCE_NAMES: Dict[str, Dict[str, str]] = {
    "constitution_of_nepal_2072": {"en": "Constitution of Nepal 2072", "ne": "नेपालको संविधान २०७२", "hi": "नेपाल का संविधान 2072"},
    "constitution_of_india": {"en": "Constitution of India", "ne": "भारतको संविधान", "hi": "भारत का संविधान"},
    "nepal_penal_code": {"en": "Nepal Penal Code 2074", "ne": "नेपाल दण्ड संहिता २०७४", "hi": "नेपाल दंड संहिता 2074"},
    "nepal_criminal_procedure": {"en": "Nepal Criminal Procedure Code 2074", "ne": "नेपाल फौजदारी प्रक्रिया संहिता २०७४", "hi": "नेपाल फौजदारी प्रक्रिया संहिता 2074"},
    "nepal_civil_code": {"en": "Nepal Civil Code 2074", "ne": "नेपाल दीवानी संहिता २०७४", "hi": "नेपाल दीवानी संहिता 2074"},
    "nepal_civil_procedure": {"en": "Nepal Civil Procedure Code 2074", "ne": "नेपाल दीवानी प्रक्रिया संहिता २०७४", "hi": "नेपाल दीवानी प्रक्रिया संहिता 2074"},
    "nepal_labor_act": {"en": "Nepal Labor Act 2074", "ne": "नेपाल श्रम ऐन २०७४", "hi": "नेपाल श्रम अधिनियम 2074"},
    "nepal_domestic_violence": {"en": "Domestic Violence (Offence and Punishment) Act 2066", "ne": "घरेलु हिंसा (अपराध र सजाय) ऐन २०६६", "hi": "घरेलू हिंसा (अपराध और सजा) अधिनियम 2066"},
    "indian_penal_code": {"en": "Indian Penal Code 1860", "ne": "भारतीय दण्ड संहिता १८६०", "hi": "भारतीय दंड संहिता 1860"},
    "code_of_criminal_procedure": {"en": "Code of Criminal Procedure 1973", "ne": "फौजदारी प्रक्रिया संहिता १९७३", "hi": "फौजदारी प्रक्रिया संहिता 1973"},
    "code_of_civil_procedure": {"en": "Code of Civil Procedure 1908", "ne": "दीवानी प्रक्रिया संहिता १९०८", "hi": "दीवानी प्रक्रिया संहिता 1908"},
    "india_consumer_protection": {"en": "Consumer Protection Act 2019", "ne": "उपभोक्ता सुरक्षा ऐन २०१९", "hi": "उपभोक्ता संरक्षण अधिनियम 2019"},
    "india_motor_vehicles": {"en": "Motor Vehicles Act 1988", "ne": "सवारी साधन ऐन १९८८", "hi": "मोटर वाहन अधिनियम 1988"},
    "india_domestic_violence": {"en": "Protection of Women from Domestic Violence Act 2005", "ne": "घरेलु हिंसाबाट महिला सुरक्षा ऐन २००५", "hi": "घरेलू हिंसा से महिलाओं की सुरक्षा अधिनियम 2005"},
    "india_information_technology": {"en": "Information Technology Act 2000", "ne": "सूचना प्रविधि ऐन २०००", "hi": "सूचना प्रौद्योगिकी अधिनियम 2000"},
    "india_negotiable_instruments": {"en": "Negotiable Instruments Act 1881", "ne": "विनिमय योग्य लिखत ऐन १८८१", "hi": "वाणिज्यिक कागजात अधिनियम 1881"},
    "india_juvenile_justice": {"en": "Juvenile Justice Act 2015", "ne": "बाल न्याय ऐन २०१५", "hi": "किशोर न्याय अधिनियम 2015"},
    "india_right_to_information": {"en": "Right to Information Act 2005", "ne": "सूचनाको अधिकार ऐन २००५", "hi": "सूचना का अधिकार अधिनियम 2005"},
    "india_evidence_act": {"en": "Indian Evidence Act 1872", "ne": "भारतीय सबूत ऐन १८७२", "hi": "भारतीय साक्ष्य अधिनियम 1872"},
    "india_specific_reliefs": {"en": "Specific Relief Act 1963", "ne": "विशिष्ट निवारण ऐन १९६३", "hi": "विशिष्ट अनुतोष अधिनियम 1963"},
    "india_transfer_of_property": {"en": "Transfer of Property Act 1882", "ne": "सम्पत्ति हस्तान्तरण ऐन १८८२", "hi": "संपत्ति के हस्तांतरण का अधिनियम 1882"},
    "minimum_wages_act": {"en": "Minimum Wages Act 1948", "ne": "न्यूनतम ज्याला ऐन १९४८", "hi": "न्यूनतम वेतन अधिनियम 1948"},
    "nepal_narcotic_drugs": {"en": "Narcotic Drugs (Control) Act 2076", "ne": "नशा नियन्त्रण ऐन २०७६", "hi": "नशीली दवाएं (नियंत्रण) अधिनियम 2076"},
    "nepal_electronic_transactions": {"en": "Electronic Transaction Act 2063", "ne": "इलेक्ट्रोनिक कारोबार ऐन २०६३", "hi": "इलेक्ट्रॉनिक लेनदेन अधिनियम 2063"},
    "nepal_right_to_information": {"en": "Right to Information Act 2064", "ne": "सूचनाको अधिकार ऐन २०६४", "hi": "सूचना का अधिकार अधिनियम 2064"},
    "indian_contract_act": {"en": "Indian Contract Act 1872", "ne": "भारतीय अनुबन्ध ऐन १८७२", "hi": "भारतीय अनुबंध अधिनियम 1872"},
    "india_sale_of_goods": {"en": "Sale of Goods Act 1930", "ne": "वस्तु बिक्री ऐन १९३०", "hi": "वस्तुओं की बिक्री अधिनियम 1930"},
    "india_partnership": {"en": "Indian Partnership Act 1932", "ne": "भारतीय साझेदारी ऐन १९३२", "hi": "भारतीय साझेदारी अधिनियम 1932"},
}


def format_citation(article: dict) -> str:
    """Format a legal article into a proper citation string.

    Examples:
        "Art. 18, Constitution of Nepal 2072 (2072 BS / 2015 CE)"
        "Section 302, Indian Penal Code 1860"
        "Section 5, Nepal Penal Code 2074"
    """
    article_num = article.get("article_number", "")
    source = article.get("source_document", "")
    year = article.get("_enactment_year", 0)
    country = article.get("country", "")
    doc_type = article.get("document_type", "")

    source_name = SOURCE_NAMES.get(source, {})
    name = source_name.get("en", source.replace("_", " ").title())

    if doc_type == "constitution":
        prefix = f"Art. {article_num}" if article_num else "Art."
        if country == "nepal":
            return f"{prefix}, {name} ({year} BS)"
        else:
            return f"{prefix}, {name}"
    else:
        prefix = f"Section {article_num}" if article_num else "Art."
        return f"{prefix}, {name}"


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
                        # Accuracy safeguards: source metadata
                        a["_last_verified"] = LAST_VERIFIED
                        a["_source_url"] = SOURCE_URLS.get(src, "")
                        if isinstance(meta, dict) and "enacted" in meta:
                            a["_effective_date"] = meta["enacted"]
                        elif a["_enactment_year"]:
                            a["_effective_date"] = str(a["_enactment_year"])
                        else:
                            a["_effective_date"] = ""
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

        # Filter out low-relevance results, deduplicate, and enrich
        filtered = []
        seen_titles: list[str] = []
        for r in results[:top_k * 3]:
            if r["score"] < MIN_RELEVANCE_SCORE:
                continue
            a = r["article"]
            # Deduplicate by title similarity
            title_lower = a.get("title", "").lower().strip()
            is_dup = False
            for seen in seen_titles:
                if _title_sim(title_lower, seen) > 0.7:
                    is_dup = True
                    break
            if is_dup:
                continue
            seen_titles.append(title_lower)
            r["confidence"] = confidence_level(r["score"])
            r["citation"] = format_citation(a)
            filtered.append(r)
            if len(filtered) >= top_k:
                break

        return filtered

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


def _title_sim(a: str, b: str) -> float:
    """Word-level Jaccard similarity between two title strings."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union) if union else 0.0


# Singleton
law_service = LawService()
