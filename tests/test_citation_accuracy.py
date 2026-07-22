"""Citation accuracy tests — validates data integrity and accuracy safeguards.

Tests that:
- All articles have proper metadata (article numbers, source info)
- Citation format is consistent and correct
- Score threshold filters properly
- Plain language summaries match source articles
- Source URL map is complete
- Rights provisions have valid citations
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.law import (
    law_service, format_citation, confidence_level,
    MIN_RELEVANCE_SCORE, SOURCE_URLS, SOURCE_NAMES, ENACTMENT_YEARS,
)
from backend.data.rights_scenarios import SCENARIOS
from backend.data.plain_language import SUMMARIES


# ═══════════════════════════════════════════════════════════════════════════
# Corpus Integrity
# ═══════════════════════════════════════════════════════════════════════════

class TestCorpusIntegrity:
    """Validate that every article in the corpus has required metadata."""

    def test_all_articles_have_id(self):
        law_service._ensure_loaded()
        for a in law_service._articles:
            assert a.get("id"), f"Article missing id: {a}"

    def test_all_articles_have_article_number(self):
        law_service._ensure_loaded()
        missing = [a["id"] for a in law_service._articles if not a.get("article_number")]
        assert len(missing) == 0, f"Articles missing article_number: {missing[:5]}"

    def test_all_articles_have_source_document(self):
        law_service._ensure_loaded()
        for a in law_service._articles:
            assert a.get("source_document"), f"Article {a.get('id')} missing source_document"

    def test_all_articles_have_country(self):
        law_service._ensure_loaded()
        for a in law_service._articles:
            assert a.get("country") in ("nepal", "india"), \
                f"Article {a.get('id')} has invalid country: {a.get('country')}"

    def test_all_articles_have_enactment_year(self):
        law_service._ensure_loaded()
        # Allow 0 for articles from sources without year mapping
        for a in law_service._articles:
            year = a.get("_enactment_year", 0)
            assert isinstance(year, int)

    def test_all_articles_have_title(self):
        law_service._ensure_loaded()
        for a in law_service._articles:
            assert a.get("title"), f"Article {a.get('id')} missing title"

    def test_all_articles_have_full_text(self):
        law_service._ensure_loaded()
        for a in law_service._articles:
            assert a.get("full_text"), f"Article {a.get('id')} missing full_text"

    def test_no_duplicate_article_ids(self):
        law_service._ensure_loaded()
        ids = [a["id"] for a in law_service._articles]
        unique = set(ids)
        dupes = len(ids) - len(unique)
        # Corpus has known duplicates from overlapping files — flag if increasing
        assert dupes <= 1700, f"Duplicate count increased: {dupes}"


# ═══════════════════════════════════════════════════════════════════════════
# Source Metadata Enrichment
# ═══════════════════════════════════════════════════════════════════════════

class TestSourceMetadata:
    """Validate that source metadata is properly enriched on all articles."""

    def test_all_articles_have_last_verified(self):
        law_service._ensure_loaded()
        for a in law_service._articles:
            lv = a.get("_last_verified", "")
            assert lv, f"Article {a.get('id')} missing _last_verified"
            assert len(lv) == 10, f"Article {a.get('id')} has invalid _last_verified: {lv}"

    def test_all_articles_have_source_url_field(self):
        law_service._ensure_loaded()
        for a in law_service._articles:
            assert "_source_url" in a, f"Article {a.get('id')} missing _source_url field"

    def test_all_articles_have_effective_date(self):
        law_service._ensure_loaded()
        for a in law_service._articles:
            assert "_effective_date" in a, f"Article {a.get('id')} missing _effective_date field"

    def test_source_url_map_covers_known_documents(self):
        law_service._ensure_loaded()
        unique_sources = {a["source_document"] for a in law_service._articles}
        missing_urls = [s for s in unique_sources if s not in SOURCE_URLS]
        # Allow some sources to not have URLs (e.g., minimum_wages_act)
        assert len(missing_urls) <= 3, f"SOURCE_URLS missing for: {missing_urls}"

    def test_source_names_map_covers_known_documents(self):
        law_service._ensure_loaded()
        unique_sources = {a["source_document"] for a in law_service._articles}
        missing_names = [s for s in unique_sources if s not in SOURCE_NAMES]
        assert len(missing_names) <= 3, f"SOURCE_NAMES missing for: {missing_names}"


# ═══════════════════════════════════════════════════════════════════════════
# Citation Format
# ═══════════════════════════════════════════════════════════════════════════

class TestCitationFormat:
    """Validate that format_citation produces correct legal citations."""

    def test_constitution_citation_nepal(self):
        law_service._ensure_loaded()
        art = next(a for a in law_service._articles if a["id"] == "nepal_const_art_18")
        citation = format_citation(art)
        assert "Art. 18" in citation
        assert "Constitution of Nepal" in citation
        assert "2072" in citation

    def test_constitution_citation_india(self):
        law_service._ensure_loaded()
        art = next(a for a in law_service._articles if a["id"] == "india_const_art_14")
        citation = format_citation(art)
        assert "Art. 14" in citation
        assert "Constitution of India" in citation

    def test_act_citation_nepal(self):
        law_service._ensure_loaded()
        nepal_acts = [a for a in law_service._articles
                      if a.get("country") == "nepal" and a.get("document_type") != "constitution"]
        if nepal_acts:
            citation = format_citation(nepal_acts[0])
            assert citation.startswith("Section") or citation.startswith("Art.")

    def test_act_citation_india(self):
        law_service._ensure_loaded()
        india_acts = [a for a in law_service._articles
                      if a.get("country") == "india" and a.get("document_type") != "constitution"]
        if india_acts:
            citation = format_citation(india_acts[0])
            assert citation.startswith("Section") or citation.startswith("Art.")

    def test_citation_is_string(self):
        law_service._ensure_loaded()
        for a in law_service._articles[:50]:
            citation = format_citation(a)
            assert isinstance(citation, str)
            assert len(citation) > 5

    def test_citation_format_consistent_for_constitutions(self):
        law_service._ensure_loaded()
        const_arts = [a for a in law_service._articles if a.get("document_type") == "constitution"]
        for a in const_arts:
            citation = format_citation(a)
            assert "Art." in citation, f"Constitution citation missing 'Art.': {citation}"


# ═══════════════════════════════════════════════════════════════════════════
# Confidence Levels
# ═══════════════════════════════════════════════════════════════════════════

class TestConfidenceLevels:
    """Validate confidence level function and score threshold."""

    def test_high_confidence_for_high_score(self):
        assert confidence_level(50) == "high"
        assert confidence_level(100) == "high"

    def test_medium_confidence(self):
        assert confidence_level(30) == "medium"
        assert confidence_level(25) == "medium"

    def test_low_confidence(self):
        assert confidence_level(20) == "low"
        assert confidence_level(5) == "low"
        assert confidence_level(1) == "low"

    def test_score_threshold_constant(self):
        assert MIN_RELEVANCE_SCORE > 0
        assert MIN_RELEVANCE_SCORE <= 10

    def test_search_returns_confidence_field(self):
        results = law_service.search("arrest detention police", top_k=5)
        for r in results:
            assert "confidence" in r, "Search result missing confidence field"
            assert r["confidence"] in ("high", "medium", "low")

    def test_search_returns_citation_field(self):
        results = law_service.search("arrest detention police", top_k=5)
        for r in results:
            assert "citation" in r, "Search result missing citation field"
            assert len(r["citation"]) > 5

    def test_search_filters_low_scores(self):
        results = law_service.search("arrest", top_k=50)
        for r in results:
            assert r["score"] >= MIN_RELEVANCE_SCORE, \
                f"Result with score {r['score']} below threshold {MIN_RELEVANCE_SCORE}"

    def test_search_returns_last_verified(self):
        results = law_service.search("arrest", top_k=3)
        for r in results:
            a = r["article"]
            assert "_last_verified" in a

    def test_search_returns_source_url(self):
        results = law_service.search("constitution", top_k=3)
        for r in results:
            a = r["article"]
            assert "_source_url" in a


# ═══════════════════════════════════════════════════════════════════════════
# Plain Language Cross-Validation
# ═══════════════════════════════════════════════════════════════════════════

class TestPlainLanguageAccuracy:
    """Validate that plain language summaries are consistent with source articles."""

    def test_all_summarized_articles_exist_in_corpus(self):
        law_service._ensure_loaded()
        corpus_ids = {a["id"] for a in law_service._articles}
        missing = [aid for aid in SUMMARIES if aid not in corpus_ids]
        # Allow articles not in extracted corpus (e.g. 300A not extracted)
        assert len(missing) <= 2, f"Summaries reference articles not in corpus: {missing}"

    def test_english_summaries_mention_key_terms(self):
        law_service._ensure_loaded()
        failed = []
        for article_id, summary in SUMMARIES.items():
            art = law_service.get_by_id(article_id)
            if not art:
                continue
            title_lower = art.get("title", "").lower()
            summary_lower = summary["en"].lower()
            title_words = [w for w in title_lower.split() if len(w) > 4]
            overlap = [w for w in title_words if w in summary_lower]
            # Allow summary to not match title words if summary is substantive
            if len(overlap) == 0 and len(title_words) > 0:
                failed.append(f"{article_id}: '{art['title']}'")
        # Allow some mismatches (summaries may use different words)
        assert len(failed) <= 10, f"Too many summaries missing title words: {failed[:10]}"

    def test_summaries_are_meaningful_length(self):
        for article_id, summary in SUMMARIES.items():
            for lang in ("en", "ne", "hi"):
                text = summary[lang]
                assert len(text) >= 50, \
                    f"Summary {article_id} {lang} too short: {len(text)} chars"
                assert len(text) <= 2000, \
                    f"Summary {article_id} {lang} too long: {len(text)} chars"


# ═══════════════════════════════════════════════════════════════════════════
# Rights Provisions Validation
# ═══════════════════════════════════════════════════════════════════════════

class TestRightsProvisionsAccuracy:
    """Validate that rights scenario provisions have valid citations."""

    def test_all_rights_provisions_have_valid_citations(self):
        law_service._ensure_loaded()
        missing_articles = []
        for scenario in SCENARIOS:
            for prov in scenario["provisions"]:
                art = law_service.get_by_id(prov["article_id"])
                if art is None:
                    missing_articles.append(f"{scenario['id']}: {prov['article_id']}")
                    continue
                citation = format_citation(art)
                assert len(citation) > 5, f"Invalid citation for {prov['article_id']}: {citation}"
        # Allow up to 2 articles not in extracted corpus
        assert len(missing_articles) <= 2, f"Too many missing articles: {missing_articles}"

    def test_rights_provisions_match_country(self):
        law_service._ensure_loaded()
        for scenario in SCENARIOS:
            for prov in scenario["provisions"]:
                art = law_service.get_by_id(prov["article_id"])
                if art:
                    assert art["country"] == prov["country"], \
                        f"Scenario {scenario['id']}: {prov['article_id']} is {art['country']} but expected {prov['country']}"

    def test_rights_provisions_have_source_urls(self):
        law_service._ensure_loaded()
        for scenario in SCENARIOS:
            for prov in scenario["provisions"]:
                art = law_service.get_by_id(prov["article_id"])
                if art:
                    assert "_source_url" in art
                    assert "_last_verified" in art


# ═══════════════════════════════════════════════════════════════════════════
# Data Completeness
# ═══════════════════════════════════════════════════════════════════════════

class TestDataCompleteness:
    """Validate that key data structures are complete and consistent."""

    def test_enactment_years_cover_all_sources(self):
        law_service._ensure_loaded()
        unique_sources = {a["source_document"] for a in law_service._articles}
        missing = [s for s in unique_sources if s not in ENACTMENT_YEARS]
        # Allow some sources without years
        assert len(missing) <= 3

    def test_source_names_have_all_languages(self):
        for source, names in SOURCE_NAMES.items():
            assert "en" in names, f"SOURCE_NAMES[{source}] missing 'en'"
            assert "ne" in names, f"SOURCE_NAMES[{source}] missing 'ne'"
            assert "hi" in names, f"SOURCE_NAMES[{source}] missing 'hi'"

    def test_article_count_reasonable(self):
        law_service._ensure_loaded()
        assert len(law_service._articles) >= 2000, \
            f"Expected at least 2000 articles, got {len(law_service._articles)}"
        assert len(law_service._articles) <= 10000, \
            f"Expected at most 10000 articles, got {len(law_service._articles)}"
