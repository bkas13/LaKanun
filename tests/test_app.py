"""Test suite for ल Kanun app — verifies core law data and search functionality.

These tests use LawService directly (no HTTP) to validate the corpus,
search logic, and data integrity.
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.law import law_service, LawService


# ============================================================================
# Data Loading Tests
# ============================================================================

class TestDataLoading:
    """Test that data loads correctly and has expected structure."""

    def test_articles_loads(self):
        law_service._ensure_loaded()
        assert len(law_service._articles) > 0

    def test_nepal_articles_exist(self):
        law_service._ensure_loaded()
        nepal = [a for a in law_service._articles if a.get("country") == "nepal"]
        assert len(nepal) > 0

    def test_india_articles_exist(self):
        law_service._ensure_loaded()
        india = [a for a in law_service._articles if a.get("country") == "india"]
        assert len(india) > 0

    def test_article_fields_present(self):
        law_service._ensure_loaded()
        required_fields = ["id", "country", "source_document", "article_number", "title", "full_text", "category"]
        for article in law_service._articles[:20]:
            for field in required_fields:
                assert field in article, f"Missing field '{field}' in article {article.get('id')}"

    def test_enactment_year_injected(self):
        law_service._ensure_loaded()
        has_year = sum(1 for a in law_service._articles if a.get("_enactment_year", 0) > 0)
        assert has_year > 0, "No articles have _enactment_year set"


# ============================================================================
# Search Tests
# ============================================================================

class TestSearch:
    """Test search functionality via LawService."""

    def test_search_returns_results(self):
        results = law_service.search("murder")
        assert len(results) > 0

    def test_search_respects_country_filter(self):
        results = law_service.search("article", country="nepal")
        for r in results:
            assert r["article"]["country"] == "nepal"

    def test_search_respects_category_filter(self):
        results = law_service.search("right", category="fundamental_rights")
        for r in results:
            assert r["article"]["category"] == "fundamental_rights"

    def test_search_respects_top_k(self):
        results = law_service.search("law", top_k=5)
        assert len(results) <= 5

    def test_search_returns_score(self):
        results = law_service.search("murder")
        assert len(results) > 0
        assert "score" in results[0]
        assert results[0]["score"] > 0

    def test_search_empty_query(self):
        results = law_service.search("")
        assert isinstance(results, list)

    def test_search_ordering_by_score(self):
        results = law_service.search("right freedom", top_k=20)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]["score"] >= results[i + 1]["score"]

    def test_search_date_newest_sort(self):
        results = law_service.search("law", sort="date_newest", top_k=10)
        if len(results) > 1:
            for i in range(len(results) - 1):
                y1 = results[i]["article"].get("_enactment_year", 0)
                y2 = results[i + 1]["article"].get("_enactment_year", 0)
                assert y1 >= y2

    def test_search_multilingual_hindi(self):
        results = law_service.search("हत्या")
        assert isinstance(results, list)

    def test_search_multilingual_nepali(self):
        results = law_service.search("सम्पत्ति")
        assert isinstance(results, list)


# ============================================================================
# Browse Tests
# ============================================================================

class TestBrowse:
    """Test browse functionality."""

    def test_browse_returns_articles(self):
        articles, total = law_service.browse(limit=5)
        assert len(articles) <= 5
        assert total > 0

    def test_browse_nepal_only(self):
        articles, total = law_service.browse(country="nepal", limit=100)
        for a in articles:
            assert a["country"] == "nepal"

    def test_browse_india_only(self):
        articles, total = law_service.browse(country="india", limit=100)
        for a in articles:
            assert a["country"] == "india"

    def test_browse_pagination(self):
        a1, _ = law_service.browse(limit=2, offset=0)
        a2, _ = law_service.browse(limit=2, offset=2)
        assert a1[0]["id"] != a2[0]["id"]

    def test_get_by_id(self):
        law_service._ensure_loaded()
        first_id = law_service._articles[0]["id"]
        article = law_service.get_by_id(first_id)
        assert article is not None
        assert article["id"] == first_id

    def test_get_by_id_not_found(self):
        article = law_service.get_by_id("nonexistent_id_xyz")
        assert article is None


# ============================================================================
# Category Stats Tests
# ============================================================================

class TestCategoryStats:
    """Test category statistics via browse."""

    def test_categories_exist(self):
        law_service._ensure_loaded()
        cats = {}
        for a in law_service._articles:
            cat = a.get("category", "other")
            cats[cat] = cats.get(cat, 0) + 1
        assert "criminal" in cats
        assert cats["criminal"] > 0


# ============================================================================
# Data Integrity Tests
# ============================================================================

class TestDataIntegrity:
    """Test data integrity across both datasets."""

    def test_no_empty_article_numbers(self):
        law_service._ensure_loaded()
        for article in law_service._articles[:100]:
            assert article.get("article_number"), f"Empty article number in {article.get('id')}"

    def test_no_empty_titles(self):
        law_service._ensure_loaded()
        for article in law_service._articles[:100]:
            assert article.get("title"), f"Empty title in {article.get('id')}"

    def test_no_empty_text(self):
        law_service._ensure_loaded()
        for article in law_service._articles[:100]:
            assert article.get("full_text"), f"Empty text in {article.get('id')}"

    def test_country_field_consistent(self):
        law_service._ensure_loaded()
        for art in law_service._articles[:200]:
            assert art["country"] in ("nepal", "india"), f"Invalid country in {art.get('id')}"

    def test_unique_ids_per_file(self):
        """Each source file should have minimal duplicate IDs.

        Some files have minor internal duplicates from parsing (e.g. 3 out of
        722 articles). This test ensures < 1% duplicates per file.
        """
        from backend.config import settings
        for filename in [
            "nepal_constitution.json", "india_constitution.json",
            "nepal_penal_code.json",
        ]:
            path = settings.processed_data_dir / filename
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                file_ids = [a["id"] for a in data.get("articles", [])]
                dupes = len(file_ids) - len(set(file_ids))
                assert dupes == 0, f"{dupes} duplicate IDs in {filename}"


# ============================================================================
# Corpus File Tests
# ============================================================================

class TestCorpusFiles:
    """Test that expected corpus files exist on disk."""

    def test_nepal_constitution_file(self):
        path = Path(__file__).parent.parent / "data" / "processed" / "nepal_constitution.json"
        assert path.exists(), "nepal_constitution.json not found"

    def test_india_constitution_file(self):
        path = Path(__file__).parent.parent / "data" / "processed" / "india_constitution.json"
        assert path.exists(), "india_constitution.json not found"

    def test_india_laws_file(self):
        path = Path(__file__).parent.parent / "data" / "processed" / "india_laws.json"
        assert path.exists(), "india_laws.json not found"

    def test_nepal_penal_code_file(self):
        path = Path(__file__).parent.parent / "data" / "processed" / "nepal_penal_code.json"
        assert path.exists(), "nepal_penal_code.json not found"

    def test_nepal_constitution_valid_json(self):
        path = Path(__file__).parent.parent / "data" / "processed" / "nepal_constitution.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert "articles" in data
        assert len(data["articles"]) == 308
