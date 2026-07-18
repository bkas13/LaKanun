"""API integration tests for all new feature endpoints.

Covers: /rights, /issues, /plain-language, /related, /feedback.
All tests use async HTTP client against the FastAPI app with in-memory DB.
"""

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.database import Base, get_db
from backend.main import create_app
from backend.models.user import User, Role
from backend.utils import hash_password

pytestmark = pytest.mark.asyncio


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
async def db():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(db: AsyncSession):
    async def override_get_db():
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    application = create_app()
    application.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def create_user(db, email, role=Role.PUBLIC):
    user = User(
        email=email, name=f"Test {email}",
        hashed_password=hash_password("testpass123"), role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(client, email):
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "testpass123"})
    return resp.json()["access_token"]


# ============================================================================
# Rights Router
# ============================================================================

class TestRightsAPI:
    async def test_list_scenarios(self, client):
        resp = await client.get("/api/v1/rights")
        assert resp.status_code == 200
        data = resp.json()
        assert "scenarios" in data
        assert len(data["scenarios"]) == 9

    async def test_list_scenarios_nepali(self, client):
        resp = await client.get("/api/v1/rights?lang=ne")
        assert resp.status_code == 200
        data = resp.json()
        titles = [s["title"] for s in data["scenarios"]]
        assert any("गिरफ्तार" in t or "अधिकार" in t for t in titles)

    async def test_list_scenarios_hindi(self, client):
        resp = await client.get("/api/v1/rights?lang=hi")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["scenarios"]) == 9

    async def test_filter_by_category(self, client):
        resp = await client.get("/api/v1/rights?category=criminal")
        assert resp.status_code == 200
        data = resp.json()
        for s in data["scenarios"]:
            assert s["category"] == "criminal"

    async def test_get_categories(self, client):
        resp = await client.get("/api/v1/rights/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert "categories" in data
        assert len(data["categories"]) > 0

    async def test_get_scenario_detail(self, client):
        resp = await client.get("/api/v1/rights/arrest")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "arrest"
        assert "your_rights" in data
        assert "deadlines" in data
        assert "where_to_go" in data
        assert "provisions" in data

    async def test_get_scenario_nepali(self, client):
        resp = await client.get("/api/v1/rights/arrest?lang=ne")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["your_rights"], list)

    async def test_get_scenario_not_found(self, client):
        resp = await client.get("/api/v1/rights/nonexistent_xyz")
        assert resp.status_code == 404

    async def test_scenario_has_all_detail_fields(self, client):
        resp = await client.get("/api/v1/rights/domestic_violence")
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == "family"
        assert len(data["your_rights"]) > 0
        assert len(data["what_authorities_must_do"]) > 0
        assert len(data["deadlines"]) > 0


# ============================================================================
# Issues Router — /issues/identify
# ============================================================================

class TestIssuesIdentifyAPI:
    async def test_identify_arrest(self, client):
        resp = await client.get("/api/v1/issues/identify?q=I+was+arrested")
        assert resp.status_code == 200
        data = resp.json()
        assert data["identified"] is True
        assert data["issue_id"] == "arrested"

    async def test_identify_domestic_violence(self, client):
        resp = await client.get("/api/v1/issues/identify?q=my+husband+beats+me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["identified"] is True
        assert data["issue_id"] == "domestic_violence"

    async def test_identify_not_found(self, client):
        resp = await client.get("/api/v1/issues/identify?q=weather+is+nice")
        assert resp.status_code == 200
        data = resp.json()
        assert data["identified"] is False

    async def test_identify_min_length(self, client):
        resp = await client.get("/api/v1/issues/identify?q=ab")
        assert resp.status_code == 422


# ============================================================================
# Issues Router — /issues/find
# ============================================================================

class TestIssuesFindAPI:
    async def test_find_arrest(self, client):
        resp = await client.get("/api/v1/issues/find?q=arrested+by+police")
        assert resp.status_code == 200
        data = resp.json()
        assert data["issue_identified"] is True
        assert len(data["search_results"]) > 0

    async def test_find_returns_guidance(self, client):
        resp = await client.get("/api/v1/issues/find?q=arrested")
        data = resp.json()
        assert isinstance(data["guidance"], str)
        assert len(data["guidance"]) > 0

    async def test_find_returns_provisions(self, client):
        resp = await client.get("/api/v1/issues/find?q=arrested")
        data = resp.json()
        assert isinstance(data["provisions"], list)
        assert len(data["provisions"]) > 0

    async def test_find_search_results_have_all_fields(self, client):
        resp = await client.get("/api/v1/issues/find?q=arrested")
        data = resp.json()
        for r in data["search_results"]:
            assert "id" in r
            assert "title" in r
            assert "country" in r
            assert "document_type" in r
            assert "enactment_year" in r
            assert "score" in r

    async def test_find_country_filter(self, client):
        resp = await client.get("/api/v1/issues/find?q=arrested&country=nepal")
        data = resp.json()
        for r in data["search_results"]:
            assert r["country"] == "nepal"

    async def test_find_nepali_lang(self, client):
        resp = await client.get("/api/v1/issues/find?q=arrested&lang=ne")
        data = resp.json()
        assert isinstance(data["guidance"], str)
        assert any(ord(c) > 0x0900 for c in data["guidance"])

    async def test_find_min_length(self, client):
        resp = await client.get("/api/v1/issues/find?q=ab")
        assert resp.status_code == 422

    async def test_find_unrecognized_issue(self, client):
        resp = await client.get("/api/v1/issues/find?q=quantum+computing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["issue_identified"] is False


# ============================================================================
# Issues Router — /plain-language
# ============================================================================

class TestPlainLanguageAPI:
    async def test_get_available_summaries(self, client):
        resp = await client.get("/api/v1/plain-language")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 25
        assert len(data["article_ids"]) >= 25

    async def test_get_summary(self, client):
        resp = await client.get("/api/v1/plain-language/nepal_const_art_16")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is True
        assert len(data["summary"]) > 0

    async def test_get_summary_nepali(self, client):
        resp = await client.get("/api/v1/plain-language/nepal_const_art_16?lang=ne")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is True

    async def test_get_summary_not_found(self, client):
        resp = await client.get("/api/v1/plain-language/nonexistent_xyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is False


# ============================================================================
# Issues Router — /related
# ============================================================================

class TestRelatedAPI:
    async def test_get_related(self, client):
        resp = await client.get("/api/v1/related/nepal_const_art_18")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        assert len(data["related"]) > 0

    async def test_related_returns_required_fields(self, client):
        resp = await client.get("/api/v1/related/nepal_const_art_18")
        data = resp.json()
        for r in data["related"]:
            assert "id" in r
            assert "title" in r
            assert "country" in r
            assert "score" in r

    async def test_related_excludes_self(self, client):
        resp = await client.get("/api/v1/related/nepal_const_art_18")
        data = resp.json()
        ids = [r["id"] for r in data["related"]]
        assert "nepal_const_art_18" not in ids

    async def test_related_respects_limit(self, client):
        resp = await client.get("/api/v1/related/nepal_const_art_18?limit=2")
        data = resp.json()
        assert len(data["related"]) <= 2

    async def test_related_not_found(self, client):
        resp = await client.get("/api/v1/related/nonexistent_xyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["related"] == []


# ============================================================================
# Feedback Router
# ============================================================================

class TestFeedbackAPI:
    async def test_vote_up(self, client):
        resp = await client.post("/api/v1/feedback/vote", json={
            "session_id": "test-session-1",
            "query": "arrest rights",
            "result_id": "nepal_const_art_18",
            "feedback": "up",
        })
        assert resp.status_code == 200
        assert resp.json()["feedback"] == "up"

    async def test_vote_down(self, client):
        resp = await client.post("/api/v1/feedback/vote", json={
            "session_id": "test-session-2",
            "query": "property law",
            "result_id": "nepal_const_art_25",
            "feedback": "down",
        })
        assert resp.status_code == 200
        assert resp.json()["feedback"] == "down"

    async def test_vote_upsert(self, client):
        await client.post("/api/v1/feedback/vote", json={
            "session_id": "test-session-3",
            "query": "test",
            "result_id": "art_1",
            "feedback": "up",
        })
        resp = await client.post("/api/v1/feedback/vote", json={
            "session_id": "test-session-3",
            "query": "test",
            "result_id": "art_1",
            "feedback": "down",
        })
        assert resp.status_code == 200
        assert resp.json()["feedback"] == "down"

    async def test_vote_invalid_feedback(self, client):
        resp = await client.post("/api/v1/feedback/vote", json={
            "session_id": "test-session-4",
            "query": "test",
            "result_id": "art_1",
            "feedback": "invalid",
        })
        assert resp.status_code == 422

    async def test_click_tracking(self, client):
        resp = await client.post("/api/v1/feedback/click", json={
            "session_id": "test-session-5",
            "query": "murder",
            "result_id": "nepal_const_art_18",
        })
        assert resp.status_code == 200

    async def test_feedback_stats(self, client):
        await client.post("/api/v1/feedback/vote", json={
            "session_id": "stats-test", "query": "test",
            "result_id": "art_1", "feedback": "up",
        })
        resp = await client.get("/api/v1/feedback/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_feedback" in data
        assert "upvotes" in data
        assert "downvotes" in data
        assert "clicks" in data

    async def test_submit_general_feedback(self, client):
        resp = await client.post("/api/v1/feedback/submit", json={
            "feedback_type": "ui",
            "subject": "Layout issue on mobile",
            "message": "The search bar is too small on iPhone screens",
        })
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    async def test_submit_invalid_type(self, client):
        resp = await client.post("/api/v1/feedback/submit", json={
            "feedback_type": "invalid_type",
            "subject": "Test",
            "message": "This is a test message with enough length",
        })
        assert resp.status_code == 422

    async def test_list_feedback_admin_only(self, client, db):
        admin = await create_user(db, "fb_admin@test.com", Role.ADMIN)
        token = await login_user(client, "fb_admin@test.com")
        resp = await client.get(
            "/api/v1/feedback/all",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    async def test_list_feedback_non_admin_blocked(self, client, db):
        pub = await create_user(db, "fb_pub@test.com", Role.PUBLIC)
        token = await login_user(client, "fb_pub@test.com")
        resp = await client.get(
            "/api/v1/feedback/all",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403


# ============================================================================
# RBAC on New Routes
# ============================================================================

class TestNewRoutesAuth:
    """Verify public access on new feature routes (no auth required)."""

    async def test_rights_public(self, client):
        resp = await client.get("/api/v1/rights")
        assert resp.status_code == 200

    async def test_rights_detail_public(self, client):
        resp = await client.get("/api/v1/rights/arrest")
        assert resp.status_code == 200

    async def test_issues_identify_public(self, client):
        resp = await client.get("/api/v1/issues/identify?q=arrested")
        assert resp.status_code == 200

    async def test_issues_find_public(self, client):
        resp = await client.get("/api/v1/issues/find?q=arrested")
        assert resp.status_code == 200

    async def test_plain_language_public(self, client):
        resp = await client.get("/api/v1/plain-language")
        assert resp.status_code == 200

    async def test_related_public(self, client):
        resp = await client.get("/api/v1/related/nepal_const_art_18")
        assert resp.status_code == 200

    async def test_feedback_vote_public(self, client):
        resp = await client.post("/api/v1/feedback/vote", json={
            "session_id": "pub-test", "query": "test",
            "result_id": "art_1", "feedback": "up",
        })
        assert resp.status_code == 200

    async def test_feedback_submit_public(self, client):
        resp = await client.post("/api/v1/feedback/submit", json={
            "feedback_type": "general",
            "subject": "Public feedback test",
            "message": "This is a public feedback test with enough length",
        })
        assert resp.status_code == 200
