"""API edge-case tests for Auth + RBAC and Feedback on new routes.

Tests: lawyer/judge access, bad tokens, missing fields, concurrent operations.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.database import Base, get_db
from backend.main import create_app
from backend.models.user import User, Role
from backend.utils import hash_password

pytestmark = pytest.mark.asyncio


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


# ═══════════════════════════════════════════════════════════════════════════
# AUTH — Edge cases
# ═══════════════════════════════════════════════════════════════════════════

class TestAuthEdgeCases:
    """Auth boundary conditions."""

    async def test_register_valid(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "new@test.com", "name": "New User", "password": "validpass123"
        })
        assert resp.status_code in (200, 201)

    async def test_register_duplicate_email(self, client, db):
        await create_user(db, "dup@test.com", Role.PUBLIC)
        resp = await client.post("/api/v1/auth/register", json={
            "email": "dup@test.com", "name": "Dup User", "password": "validpass123"
        })
        assert resp.status_code in (400, 409, 422)

    async def test_register_short_password(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "short@test.com", "name": "Short", "password": "123"
        })
        assert resp.status_code in (400, 422)

    async def test_login_valid(self, client, db):
        await create_user(db, "login@test.com", Role.PUBLIC)
        resp = await client.post("/api/v1/auth/login", json={
            "email": "login@test.com", "password": "testpass123"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_wrong_password(self, client, db):
        await create_user(db, "wrongpw@test.com", Role.PUBLIC)
        resp = await client.post("/api/v1/auth/login", json={
            "email": "wrongpw@test.com", "password": "wrongpassword"
        })
        assert resp.status_code in (401, 403)

    async def test_login_nonexistent_user(self, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@test.com", "password": "whatever123"
        })
        assert resp.status_code in (401, 403)

    async def test_invalid_token_rejected(self, client):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer totally.invalid.token"}
        )
        assert resp.status_code == 401

    async def test_no_authorization_header(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_malformed_bearer_token(self, client):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "NotBearer token"}
        )
        assert resp.status_code == 401

    async def test_empty_bearer_token(self, client):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer "}
        )
        assert resp.status_code in (401, 403)


# ═══════════════════════════════════════════════════════════════════════════
# RBAC — New routes with different roles
# ═══════════════════════════════════════════════════════════════════════════

class TestRBACNewRoutes:
    """Test that new feature routes allow all roles (public access)."""

    async def test_lawyer_can_access_rights(self, client, db):
        await create_user(db, "law@test.com", Role.LAWYER)
        token = await login_user(client, "law@test.com")
        resp = await client.get("/api/v1/rights", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    async def test_judge_can_access_rights(self, client, db):
        await create_user(db, "judge@test.com", Role.JUDGE)
        token = await login_user(client, "judge@test.com")
        resp = await client.get("/api/v1/rights", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    async def test_admin_can_access_rights(self, client, db):
        await create_user(db, "adm@test.com", Role.ADMIN)
        token = await login_user(client, "adm@test.com")
        resp = await client.get("/api/v1/rights", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    async def test_public_can_access_rights_no_token(self, client):
        resp = await client.get("/api/v1/rights")
        assert resp.status_code == 200

    async def test_lawyer_can_access_issues(self, client, db):
        await create_user(db, "law2@test.com", Role.LAWYER)
        token = await login_user(client, "law2@test.com")
        resp = await client.get("/api/v1/issues/identify?q=arrested", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    async def test_lawyer_can_access_related(self, client, db):
        await create_user(db, "law3@test.com", Role.LAWYER)
        token = await login_user(client, "law3@test.com")
        resp = await client.get("/api/v1/related/nepal_const_art_18", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    async def test_lawyer_can_access_plain_language(self, client, db):
        await create_user(db, "law4@test.com", Role.LAWYER)
        token = await login_user(client, "law4@test.com")
        resp = await client.get("/api/v1/plain-language", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    async def test_lawyer_can_vote_feedback(self, client, db):
        await create_user(db, "law5@test.com", Role.LAWYER)
        token = await login_user(client, "law5@test.com")
        resp = await client.post("/api/v1/feedback/vote", json={
            "session_id": "lawyer-vote", "query": "test",
            "result_id": "art_1", "feedback": "up"
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════
# FEEDBACK — Edge cases
# ═══════════════════════════════════════════════════════════════════════════

class TestFeedbackEdgeCases:
    """Feedback boundary conditions and error paths."""

    async def test_vote_missing_session_id(self, client):
        resp = await client.post("/api/v1/feedback/vote", json={
            "query": "test", "result_id": "art_1", "feedback": "up"
        })
        assert resp.status_code == 422

    async def test_vote_missing_result_id(self, client):
        resp = await client.post("/api/v1/feedback/vote", json={
            "session_id": "s1", "query": "test", "feedback": "up"
        })
        assert resp.status_code == 422

    async def test_vote_missing_feedback_field(self, client):
        resp = await client.post("/api/v1/feedback/vote", json={
            "session_id": "s1", "query": "test", "result_id": "art_1"
        })
        assert resp.status_code == 422

    async def test_vote_empty_session_id(self, client):
        resp = await client.post("/api/v1/feedback/vote", json={
            "session_id": "", "query": "test", "result_id": "art_1", "feedback": "up"
        })
        assert resp.status_code in (400, 422)

    async def test_vote_empty_result_id(self, client):
        resp = await client.post("/api/v1/feedback/vote", json={
            "session_id": "s1", "query": "test", "result_id": "", "feedback": "up"
        })
        assert resp.status_code in (200, 400, 422)

    async def test_click_missing_fields(self, client):
        resp = await client.post("/api/v1/feedback/click", json={
            "session_id": "s1"
        })
        assert resp.status_code == 422

    async def test_click_empty_session_id(self, client):
        resp = await client.post("/api/v1/feedback/click", json={
            "session_id": "", "query": "test", "result_id": "art_1"
        })
        assert resp.status_code in (400, 422)

    async def test_feedback_submit_missing_fields(self, client):
        resp = await client.post("/api/v1/feedback/submit", json={
            "feedback_type": "ui"
        })
        assert resp.status_code == 422

    async def test_feedback_submit_empty_message(self, client):
        resp = await client.post("/api/v1/feedback/submit", json={
            "feedback_type": "ui", "subject": "Test", "message": ""
        })
        assert resp.status_code in (400, 422)

    async def test_vote_same_session_different_results(self, client):
        for i in range(3):
            resp = await client.post("/api/v1/feedback/vote", json={
                "session_id": "multi-session", "query": "test",
                "result_id": f"art_{i}", "feedback": "up"
            })
            assert resp.status_code == 200

    async def test_feedback_stats_structure(self, client):
        resp = await client.get("/api/v1/feedback/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["total_feedback"], int)
        assert isinstance(data["upvotes"], int)
        assert isinstance(data["downvotes"], int)
        assert isinstance(data["clicks"], int)

    async def test_list_feedback_requires_admin(self, client, db):
        await create_user(db, "nonadm@test.com", Role.LAWYER)
        token = await login_user(client, "nonadm@test.com")
        resp = await client.get(
            "/api/v1/feedback/all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 403

    async def test_list_feedback_requires_auth(self, client):
        resp = await client.get("/api/v1/feedback/all")
        assert resp.status_code in (401, 403)


# ═══════════════════════════════════════════════════════════════════════════
# API Input Validation — Boundary lengths
# ═══════════════════════════════════════════════════════════════════════════

class TestInputValidation:
    """Test query length validation on new routes."""

    async def test_issues_identify_too_short(self, client):
        resp = await client.get("/api/v1/issues/identify?q=ab")
        assert resp.status_code == 422

    async def test_issues_find_too_short(self, client):
        resp = await client.get("/api/v1/issues/find?q=ab")
        assert resp.status_code == 422

    async def test_issues_identify_single_char(self, client):
        resp = await client.get("/api/v1/issues/identify?q=a")
        assert resp.status_code == 422

    async def test_issues_identify_exact_min(self, client):
        resp = await client.get("/api/v1/issues/identify?q=abc")
        assert resp.status_code == 200

    async def test_rights_no_validation_on_list(self, client):
        resp = await client.get("/api/v1/rights")
        assert resp.status_code == 200

    async def test_related_no_validation_on_list(self, client):
        resp = await client.get("/api/v1/related/nepal_const_art_18")
        assert resp.status_code == 200
