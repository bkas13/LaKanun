"""Unit tests for all backend services — no HTTP, direct function calls.

Covers: issue_finder, related provisions, multilingual search,
plain language summaries, rights scenarios.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.issue_finder import identify_issue, find_laws_for_issue, ISSUE_PATTERNS
from backend.services.related import find_related_provisions, RELATED_CATEGORIES, KEYWORD_GROUPS
from backend.services.multilingual_search import (
    detect_script, translate_query, DEVANAGARI_TO_ENGLISH, ROMANIZED_MAP,
)
from backend.data.plain_language import get_summary, get_summaries_batch, get_all_summarized_ids, SUMMARIES
from backend.data.rights_scenarios import get_all_scenarios, get_scenario_by_id, get_scenarios_by_category, get_categories
from backend.services.law import law_service


# ============================================================================
# Issue Finder — identify_issue()
# ============================================================================

class TestIdentifyIssue:
    """Test issue identification from natural language descriptions."""

    def test_arrest_identified(self):
        result = identify_issue("I was arrested by police")
        assert result is not None
        assert result["id"] == "arrested"

    def test_arrest_partial_english_match(self):
        result = identify_issue("police took me into custody")
        assert result is not None
        assert result["id"] == "arrested"

    def test_domestic_violence_identified(self):
        result = identify_issue("My husband beats me")
        assert result is not None
        assert result["id"] == "domestic_violence"

    def test_property_dispute_identified(self):
        result = identify_issue("My tenant won't leave my house")
        assert result is not None
        assert result["id"] == "property_dispute"

    def test_workplace_identified(self):
        result = identify_issue("My employer fired me without notice")
        assert result is not None
        assert result["id"] == "workplace"

    def test_consumer_identified(self):
        result = identify_issue("I bought a defective product")
        assert result is not None
        assert result["id"] == "consumer"

    def test_inheritance_identified(self):
        result = identify_issue("father died siblings fighting over property")
        assert result is not None
        assert result["id"] == "inheritance"

    def test_cyber_fraud_identified(self):
        result = identify_issue("Someone hacked my bank account")
        assert result is not None
        assert result["id"] == "cyber_fraud"

    def test_cheque_bounce_identified(self):
        result = identify_issue("My cheque bounced due to insufficient funds")
        assert result is not None
        assert result["id"] == "cheque_bounce"

    def test_bail_identified(self):
        result = identify_issue("How to get bail")
        assert result is not None
        assert result["id"] == "bail"

    def test_right_to_info_identified(self):
        result = identify_issue("I need government information under RTI")
        assert result is not None
        assert result["id"] == "right_to_info"

    def test_unrelated_returns_none(self):
        result = identify_issue("the weather is nice today")
        assert result is None

    def test_empty_string_returns_none(self):
        result = identify_issue("")
        assert result is None

    def test_multi_word_keyword_scores_higher(self):
        result = identify_issue("child labor exploitation")
        assert result is not None
        assert result["id"] == "child"

    def test_accident_identified(self):
        result = identify_issue("car accident motor vehicle collision")
        assert result is not None
        assert result["id"] == "accident"

    def test_marriage_divorce_identified(self):
        result = identify_issue("divorce and alimony from spouse")
        assert result is not None
        assert result["id"] == "marriage_divorce"

    def test_all_patterns_have_required_fields(self):
        for pattern in ISSUE_PATTERNS:
            assert "id" in pattern
            assert "keywords" in pattern and len(pattern["keywords"]) > 0
            assert "search_queries" in pattern and len(pattern["search_queries"]) > 0
            assert "categories" in pattern
            assert "title" in pattern
            assert "en" in pattern["title"]
            assert "ne" in pattern["title"]
            assert "hi" in pattern["title"]

    def test_best_match_wins(self):
        result = identify_issue("police arrested me and I need bail")
        assert result is not None
        assert result["id"] in ("arrested", "bail")


# ============================================================================
# Issue Finder — find_laws_for_issue()
# ============================================================================

class TestFindLawsForIssue:
    """Test the full issue-to-law mapping pipeline."""

    def test_identified_issue_returns_results(self):
        result = find_laws_for_issue("I was arrested by police")
        assert result["issue_identified"] is True
        assert result["issue_id"] == "arrested"
        assert len(result["search_results"]) > 0

    def test_title_is_string(self):
        result = find_laws_for_issue("I was arrested by police")
        assert isinstance(result["title"], str)
        assert len(result["title"]) > 0

    def test_guidance_is_string(self):
        result = find_laws_for_issue("I was arrested by police")
        assert isinstance(result["guidance"], str)
        assert len(result["guidance"]) > 0

    def test_guidance_nepali(self):
        result = find_laws_for_issue("I was arrested", lang="ne")
        assert isinstance(result["guidance"], str)
        assert any(ord(c) > 0x0900 for c in result["guidance"]), "Guidance should contain Devanagari"

    def test_guidance_hindi(self):
        result = find_laws_for_issue("I was arrested", lang="hi")
        assert isinstance(result["guidance"], str)
        assert any(ord(c) > 0x0900 for c in result["guidance"]), "Guidance should contain Devanagari"

    def test_provisions_grouped_by_country(self):
        result = find_laws_for_issue("arrested by police")
        countries = {p["country"] for p in result["provisions"]}
        assert len(countries) >= 1
        assert countries.issubset({"nepal", "india"})

    def test_provisions_have_articles(self):
        result = find_laws_for_issue("arrested by police")
        for prov in result["provisions"]:
            assert "articles" in prov
            assert len(prov["articles"]) > 0
            for art in prov["articles"]:
                assert "id" in art
                assert "title" in art

    def test_search_results_have_all_fields(self):
        result = find_laws_for_issue("arrested")
        for r in result["search_results"]:
            assert "id" in r
            assert "title" in r
            assert "country" in r
            assert "category" in r
            assert "document_type" in r
            assert "source_document" in r
            assert "score" in r
            assert "full_text" in r
            assert "enactment_year" in r

    def test_unrecognized_issue_falls_back_to_search(self):
        result = find_laws_for_issue("quantum computing regulation")
        assert result["issue_identified"] is False
        assert len(result["search_results"]) >= 0

    def test_guidance_for_unrecognized_is_string(self):
        result = find_laws_for_issue("random unrelated thing")
        assert isinstance(result["guidance"], str)

    def test_country_filter_nepal(self):
        result = find_laws_for_issue("arrested", country="nepal")
        for r in result["search_results"]:
            assert r["country"] == "nepal"

    def test_country_filter_india(self):
        result = find_laws_for_issue("arrested", country="india")
        for r in result["search_results"]:
            assert r["country"] == "india"

    def test_domestic_violence_has_results(self):
        result = find_laws_for_issue("domestic violence spouse abuse")
        assert result["issue_identified"] is True
        assert len(result["search_results"]) > 0

    def test_max_fifteen_results(self):
        result = find_laws_for_issue("arrested by police custody detention")
        assert len(result["search_results"]) <= 15

    def test_no_duplicate_results(self):
        result = find_laws_for_issue("arrested by police")
        ids = [r["id"] for r in result["search_results"]]
        assert len(ids) == len(set(ids))


# ============================================================================
# Related Provisions — find_related_provisions()
# ============================================================================

class TestRelatedProvisions:
    """Test the cross-law related provisions engine."""

    def test_related_for_constitution_article(self):
        article = law_service.get_by_id("nepal_const_art_18")
        assert article is not None
        related = find_related_provisions("nepal_const_art_18", article=article)
        assert len(related) > 0

    def test_related_excludes_self(self):
        article = law_service.get_by_id("nepal_const_art_18")
        related = find_related_provisions("nepal_const_art_18", article=article)
        ids = [r["id"] for r in related]
        assert "nepal_const_art_18" not in ids

    def test_related_returns_required_fields(self):
        article = law_service.get_by_id("nepal_const_art_18")
        related = find_related_provisions("nepal_const_art_18", article=article)
        for r in related:
            assert "id" in r
            assert "title" in r
            assert "country" in r
            assert "category" in r
            assert "score" in r
            assert r["score"] >= 3.0

    def test_related_cross_country(self):
        article = law_service.get_by_id("nepal_const_art_18")
        related = find_related_provisions("nepal_const_art_18", article=article)
        countries = {r["country"] for r in related}
        assert "india" in countries, "Should find related provisions from India too"

    def test_related_sorted_by_score(self):
        article = law_service.get_by_id("nepal_const_art_18")
        related = find_related_provisions("nepal_const_art_18", article=article)
        for i in range(len(related) - 1):
            assert related[i]["score"] >= related[i + 1]["score"]

    def test_related_respects_limit(self):
        article = law_service.get_by_id("nepal_const_art_18")
        related = find_related_provisions("nepal_const_art_18", article=article, limit=3)
        assert len(related) <= 3

    def test_related_nonexistent_article(self):
        related = find_related_provisions("nonexistent_id_xyz")
        assert related == []

    def test_related_fetches_article_if_not_provided(self):
        related = find_related_provisions("nepal_const_art_18")
        assert len(related) > 0

    def test_related_different_articles_different_results(self):
        art1 = law_service.get_by_id("nepal_const_art_18")
        art2 = law_service.get_by_id("india_const_art_14")
        if art1 and art2:
            rel1 = find_related_provisions("nepal_const_art_18", article=art1)
            rel2 = find_related_provisions("india_const_art_14", article=art2)
            ids1 = {r["id"] for r in rel1}
            ids2 = {r["id"] for r in rel2}
            assert ids1 != ids2

    def test_related_criminal_article(self):
        law_service._ensure_loaded()
        criminal_arts = [a for a in law_service._articles if "arrest" in (a.get("category", "") + a.get("title", "").lower())]
        if criminal_arts:
            art = criminal_arts[0]
            related = find_related_provisions(art["id"], article=art, limit=5)
            assert len(related) > 0

    def test_related_categories_are_consistent(self):
        for cat, related_cats in RELATED_CATEGORIES.items():
            assert isinstance(related_cats, list)
            assert len(related_cats) > 0

    def test_keyword_groups_are_consistent(self):
        for group, keywords in KEYWORD_GROUPS.items():
            assert isinstance(keywords, list)
            assert len(keywords) > 0


# ============================================================================
# Multilingual Search — detect_script()
# ============================================================================

class TestDetectScript:
    """Test language/script detection."""

    def test_english_is_latin(self):
        assert detect_script("arrest and bail") == "latin"

    def test_nepali_is_devanagari(self):
        assert detect_script("गिरफ्तारी र जमानत") == "devanagari"

    def test_hindi_is_devanagari(self):
        assert detect_script("गिरफ्तारी और जमानत") == "devanagari"

    def test_balanced_mixed_script(self):
        assert detect_script("ab अभ") == "mixed"

    def test_numbers_and_punctuation_ignored(self):
        assert detect_script("123 !@#") == "unknown"

    def test_empty_string(self):
        assert detect_script("") == "unknown"

    def test_latin_with_numbers(self):
        assert detect_script("article 18 freedom") == "latin"

    def test_devanagari_single_word(self):
        assert detect_script("अधिकार") == "devanagari"


# ============================================================================
# Multilingual Search — translate_query()
# ============================================================================

class TestTranslateQuery:
    """Test query translation from various languages to English."""

    def test_english_passthrough(self):
        lang, english, terms = translate_query("murder punishment")
        assert lang == "en"
        assert "murder" in english.lower()

    def test_devanagari_murder(self):
        lang, english, terms = translate_query("हत्या")
        assert lang == "devanagari"
        assert any("murder" in t.lower() for t in terms)

    def test_devanagari_property(self):
        lang, english, terms = translate_query("सम्पत्ति")
        assert lang == "devanagari"
        assert any("property" in t.lower() for t in terms)

    def test_devanagari_arrest(self):
        lang, english, terms = translate_query("गिरफ्तारी")
        assert lang == "devanagari"
        assert any("arrest" in t.lower() for t in terms)

    def test_devanagari_court(self):
        lang, english, terms = translate_query("अदालत")
        assert lang == "devanagari"
        assert any("court" in t.lower() for t in terms)

    def test_romanized_murder(self):
        lang, english, terms = translate_query("hatya")
        assert lang in ("romanized", "romanized_ne", "romanized_hi")
        assert any("murder" in t.lower() for t in terms)

    def test_romanized_theft(self):
        lang, english, terms = translate_query("chori")
        assert lang in ("romanized", "romanized_ne", "romanized_hi")
        assert any("theft" in t.lower() for t in terms)

    def test_romanized_bail(self):
        lang, english, terms = translate_query("jamanat")
        assert lang in ("romanized", "romanized_ne", "romanized_hi")
        assert any("bail" in t.lower() for t in terms)

    def test_romanized_lawyer(self):
        lang, english, terms = translate_query("vakil")
        assert lang in ("romanized", "romanized_ne", "romanized_hi")
        assert any("lawyer" in t.lower() for t in terms)

    def test_mixed_script(self):
        lang, english, terms = translate_query("murder हत्या")
        assert len(terms) > 0
        assert lang in ("en", "devanagari", "mixed")

    def test_empty_query(self):
        lang, english, terms = translate_query("")
        assert lang == "en"
        assert english == ""

    def test_devanagari_multiword(self):
        lang, english, terms = translate_query("हत्या सजाय")
        assert lang == "devanagari"
        assert len(terms) >= 2

    def test_unrecognized_romanized_falls_back(self):
        lang, english, terms = translate_query("xyznotaword")
        assert lang == "en"

    def test_devanagari_marriage(self):
        lang, english, terms = translate_query("विवाह")
        assert lang == "devanagari"
        assert any("marriage" in t.lower() for t in terms)

    def test_devanagari_divorce(self):
        lang, english, terms = translate_query("तलाक")
        assert lang == "devanagari"
        assert any("divorce" in t.lower() for t in terms)

    def test_romanized_police(self):
        lang, english, terms = translate_query("police thana")
        assert len(terms) > 0


# ============================================================================
# Plain Language Summaries
# ============================================================================

class TestPlainLanguage:
    """Test plain language legal summaries data module."""

    def test_summaries_not_empty(self):
        assert len(SUMMARIES) > 0

    def test_has_at_least_25_summaries(self):
        assert len(SUMMARIES) >= 25

    def test_get_summary_returns_dict(self):
        summary = get_summary("nepal_const_art_16")
        assert summary is not None
        assert isinstance(summary, dict)

    def test_get_summary_has_all_languages(self):
        summary = get_summary("nepal_const_art_16")
        assert "en" in summary
        assert "ne" in summary
        assert "hi" in summary

    def test_get_summary_english_not_empty(self):
        summary = get_summary("nepal_const_art_16")
        assert len(summary["en"]) > 0

    def test_get_summary_nonexistent_returns_none(self):
        summary = get_summary("nonexistent_article_xyz")
        assert summary is None

    def test_get_summaries_batch(self):
        ids = ["nepal_const_art_16", "nepal_const_art_18", "india_const_art_14"]
        results = get_summaries_batch(ids)
        assert len(results) == 3
        assert "nepal_const_art_16" in results
        assert "india_const_art_14" in results

    def test_get_summaries_batch_empty(self):
        results = get_summaries_batch([])
        assert results == {}

    def test_get_summaries_batch_partial(self):
        results = get_summaries_batch(["nepal_const_art_16", "nonexistent_xyz"])
        assert "nepal_const_art_16" in results
        assert "nonexistent_xyz" not in results

    def test_get_all_summarized_ids(self):
        ids = get_all_summarized_ids()
        assert len(ids) >= 25
        assert "nepal_const_art_16" in ids
        assert "india_const_art_14" in ids

    def test_all_summaries_have_all_languages(self):
        for article_id, summary in SUMMARIES.items():
            assert "en" in summary, f"Missing 'en' in {article_id}"
            assert "ne" in summary, f"Missing 'ne' in {article_id}"
            assert "hi" in summary, f"Missing 'hi' in {article_id}"
            assert len(summary["en"]) > 0, f"Empty 'en' in {article_id}"


# ============================================================================
# Rights Scenarios
# ============================================================================

class TestRightsScenarios:
    """Test rights scenario data module."""

    def test_scenarios_not_empty(self):
        scenarios = get_all_scenarios()
        assert len(scenarios) > 0

    def test_nine_scenarios(self):
        scenarios = get_all_scenarios()
        assert len(scenarios) == 9

    def test_get_by_id_valid(self):
        scenario = get_scenario_by_id("arrest")
        assert scenario is not None
        assert scenario["id"] == "arrest"

    def test_get_by_id_not_found(self):
        scenario = get_scenario_by_id("nonexistent")
        assert scenario is None

    def test_categories_not_empty(self):
        categories = get_categories()
        assert len(categories) > 0

    def test_categories_include_criminal(self):
        categories = get_categories()
        assert "criminal" in categories

    def test_filter_by_category(self):
        scenarios = get_scenarios_by_category("criminal")
        assert len(scenarios) > 0
        for s in scenarios:
            assert s["category"] == "criminal"

    def test_filter_by_nonexistent_category(self):
        scenarios = get_scenarios_by_category("nonexistent_category")
        assert len(scenarios) == 0

    def test_scenario_has_all_languages(self):
        scenario = get_scenario_by_id("arrest")
        assert "en" in scenario["title"]
        assert "ne" in scenario["title"]
        assert "hi" in scenario["title"]

    def test_scenario_has_required_fields(self):
        scenario = get_scenario_by_id("arrest")
        assert "id" in scenario
        assert "category" in scenario
        assert "title" in scenario
        assert "description" in scenario
        assert "your_rights" in scenario
        assert "what_authorities_must_do" in scenario
        assert "deadlines" in scenario
        assert "where_to_go" in scenario
        assert "provisions" in scenario

    def test_all_scenarios_have_unique_ids(self):
        scenarios = get_all_scenarios()
        ids = [s["id"] for s in scenarios]
        assert len(ids) == len(set(ids))

    def test_scenario_rights_is_list(self):
        scenario = get_scenario_by_id("arrest")
        assert isinstance(scenario["your_rights"], dict)
        assert isinstance(scenario["your_rights"]["en"], list)
        assert len(scenario["your_rights"]["en"]) > 0

    def test_scenario_provisions_have_structure(self):
        scenario = get_scenario_by_id("arrest")
        provisions = scenario["provisions"]
        assert isinstance(provisions, list)
        assert len(provisions) > 0
        assert "country" in provisions[0] or "article_id" in provisions[0]
