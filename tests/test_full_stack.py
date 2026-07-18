"""Comprehensive tests — search, browse, stats, auth flow, saved items, admin."""

import asyncio
import tempfile
from pathlib import Path

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


async def create_user(db, email, role=Role.PUBLIC, password="testpass123"):
    user = User(
        email=email,
        name=f"User {email}",
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def register(client, name="Test User", email="test@test.com", password="testpass123"):
    resp = await client.post("/api/v1/auth/register", json={
        "name": name, "email": email, "password": password,
    })
    return resp


async def login(client, email="test@test.com", password="testpass123"):
    resp = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password,
    })
    return resp.json()


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# 1. PUBLIC SEARCH — no auth required
# ============================================================================

class TestPublicSearch:
    async def test_search_without_auth(self, client):
        """Search must work without login."""
        resp = await client.get("/api/v1/laws/search?q=murder&top_k=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        assert len(data["results"]) > 0

    async def test_search_returns_relevant_results(self, client):
        resp = await client.get("/api/v1/laws/search?q=property+rights&top_k=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        for r in data["results"]:
            assert "score" in r
            assert r["score"] > 0
            assert "title" in r
            assert "country" in r

    async def test_search_with_country_filter(self, client):
        resp = await client.get("/api/v1/laws/search?q=contract&country=nepal&top_k=5")
        assert resp.status_code == 200
        data = resp.json()
        for r in data["results"]:
            assert r["country"] == "nepal"

    async def test_search_various_queries(self, client):
        for q in ["divorce", "murder", "property", "labor", "tax", "adoption", "bail"]:
            resp = await client.get(f"/api/v1/laws/search?q={q}&top_k=3")
            assert resp.status_code == 200, f"Failed for query: {q}"

    async def test_search_too_short_query(self, client):
        resp = await client.get("/api/v1/laws/search?q=a")
        assert resp.status_code == 422

    async def test_search_results_have_required_fields(self, client):
        resp = await client.get("/api/v1/laws/search?q=custody&top_k=2")
        data = resp.json()
        if data["results"]:
            r = data["results"][0]
            for field in ["id", "title", "full_text", "country", "category", "score"]:
                assert field in r, f"Missing field: {field}"


# ============================================================================
# 2. PUBLIC BROWSE — no auth required
# ============================================================================

class TestPublicBrowse:
    async def test_browse_without_auth(self, client):
        resp = await client.get("/api/v1/laws/browse?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0

    async def test_browse_nepal(self, client):
        resp = await client.get("/api/v1/laws/browse?country=nepal&limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0

    async def test_browse_india(self, client):
        resp = await client.get("/api/v1/laws/browse?country=india&limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0

    async def test_browse_all_provisions(self, client):
        resp = await client.get("/api/v1/laws/browse?limit=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 6242

    async def test_browse_pagination(self, client):
        resp1 = await client.get("/api/v1/laws/browse?limit=2&offset=0")
        resp2 = await client.get("/api/v1/laws/browse?limit=2&offset=2")
        d1 = resp1.json()
        d2 = resp2.json()
        assert d1["articles"][0]["id"] != d2["articles"][0]["id"]


# ============================================================================
# 3. PUBLIC STATS — no auth required
# ============================================================================

class TestPublicStats:
    async def test_stats_without_auth(self, client):
        resp = await client.get("/api/v1/laws/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_provisions"] == 6242
        assert data["nepal"] > 0
        assert data["india"] > 0
        assert len(data["top_categories"]) > 0

    async def test_stats_country_counts(self, client):
        data = (await client.get("/api/v1/laws/stats")).json()
        assert data["nepal"] == 2655
        assert data["india"] == 3587
        assert data["nepal"] + data["india"] == data["total_provisions"]


# ============================================================================
# 4. AUTH FLOW — register → login → me → refresh
# ============================================================================

class TestAuthFlow:
    async def test_full_register_login_me_flow(self, client):
        # Register
        reg = await register(client, name="Flow User", email="flow@test.com", password="securepass123")
        assert reg.status_code == 201
        tokens = reg.json()
        assert "access_token" in tokens
        assert tokens["user"]["name"] == "Flow User"
        assert tokens["user"]["role"] == "public"

        # Me
        me = await client.get("/api/v1/auth/me", headers=auth_header(tokens["access_token"]))
        assert me.status_code == 200
        assert me.json()["email"] == "flow@test.com"

        # Refresh
        refresh = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": tokens["refresh_token"],
        })
        assert refresh.status_code == 200
        new_tokens = refresh.json()
        assert "access_token" in new_tokens

        # Me with new token
        me2 = await client.get("/api/v1/auth/me", headers=auth_header(new_tokens["access_token"]))
        assert me2.status_code == 200

    async def test_login_wrong_password(self, client, db):
        await create_user(db, "wp@test.com")
        resp = await client.post("/api/v1/auth/login", json={
            "email": "wp@test.com", "password": "wrongpassword",
        })
        assert resp.status_code == 401

    async def test_register_duplicate_email(self, client, db):
        await create_user(db, "dup@test.com")
        resp = await register(client, email="dup@test.com")
        assert resp.status_code == 409

    async def test_register_short_password(self, client):
        resp = await register(client, email="short@test.com", password="123")
        assert resp.status_code == 422

    async def test_me_without_token(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 403)


# ============================================================================
# 5. BOOKMARKS CRUD — lawyer only
# ============================================================================

class TestBookmarks:
    async def test_lawyer_full_crud(self, client, db):
        user = await create_user(db, "bm@test.com", Role.LAWYER)
        tokens = await login(client, "bm@test.com")
        h = auth_header(tokens["access_token"])

        # Create
        create = await client.post("/api/v1/saved/bookmarks", json={
            "provision_id": "nepal_constitution_art_16",
            "country": "nepal",
            "title": "Right to Equality",
            "note": "Important for gender cases",
        }, headers=h)
        assert create.status_code == 201
        bm_id = create.json()["id"]

        # List
        listing = await client.get("/api/v1/saved/bookmarks", headers=h)
        assert listing.status_code == 200
        assert len(listing.json()) >= 1

        # Delete
        delete = await client.delete(f"/api/v1/saved/bookmarks/{bm_id}", headers=h)
        assert delete.status_code == 204

    async def test_public_cannot_bookmark(self, client, db):
        user = await create_user(db, "nobm@test.com", Role.PUBLIC)
        tokens = await login(client, "nobm@test.com")
        resp = await client.get("/api/v1/saved/bookmarks",
                                headers=auth_header(tokens["access_token"]))
        assert resp.status_code == 403


# ============================================================================
# 6. CASE NOTES CRUD — lawyer only
# ============================================================================

class TestCaseNotes:
    async def test_lawyer_full_note_crud(self, client, db):
        user = await create_user(db, "cn@test.com", Role.LAWYER)
        tokens = await login(client, "cn@test.com")
        h = auth_header(tokens["access_token"])

        # Create
        create = await client.post("/api/v1/saved/notes", json={
            "title": "Case v. Sharma",
            "content": "Key arguments about property rights under Article 25.",
            "tags": ["property", "constitutional"],
        }, headers=h)
        assert create.status_code == 201
        note_id = create.json()["id"]

        # List
        listing = await client.get("/api/v1/saved/notes", headers=h)
        assert listing.status_code == 200

        # Update
        update = await client.put(f"/api/v1/saved/notes/{note_id}", json={
            "content": "Updated arguments.",
        }, headers=h)
        assert update.status_code == 200
        assert update.json()["content"] == "Updated arguments."

        # Delete
        delete = await client.delete(f"/api/v1/saved/notes/{note_id}", headers=h)
        assert delete.status_code == 204


# ============================================================================
# 7. SEARCH HISTORY — authenticated users
# ============================================================================

class TestSearchHistory:
    async def test_create_and_list_history(self, client, db):
        user = await create_user(db, "sh@test.com")
        tokens = await login(client, "sh@test.com")
        h = auth_header(tokens["access_token"])

        # Create
        create = await client.post("/api/v1/saved/search-history", json={
            "query": "property rights",
            "country": "nepal",
            "results_count": 15,
        }, headers=h)
        assert create.status_code == 201

        # List
        listing = await client.get("/api/v1/saved/search-history", headers=h)
        assert listing.status_code == 200
        assert len(listing.json()) >= 1

        # Suggestions
        suggestions = await client.get("/api/v1/saved/search-suggestions", headers=h)
        assert suggestions.status_code == 200

    async def test_unauthenticated_cannot_track_history(self, client):
        resp = await client.post("/api/v1/saved/search-history", json={
            "query": "test",
        })
        assert resp.status_code in (401, 403)


# ============================================================================
# 8. ADMIN — admin only
# ============================================================================

class TestAdmin:
    async def test_admin_users_and_stats(self, client, db):
        admin = await create_user(db, "admin@test.com", Role.ADMIN)
        tokens = await login(client, "admin@test.com")
        h = auth_header(tokens["access_token"])

        # Users
        users = await client.get("/api/v1/admin/users", headers=h)
        assert users.status_code == 200
        assert len(users.json()) >= 1

        # Stats
        stats = await client.get("/api/v1/admin/stats", headers=h)
        assert stats.status_code == 200

    async def test_non_admin_blocked(self, client, db):
        user = await create_user(db, "na@test.com", Role.PUBLIC)
        tokens = await login(client, "na@test.com")
        resp = await client.get("/api/v1/admin/users",
                                headers=auth_header(tokens["access_token"]))
        assert resp.status_code == 403


# ============================================================================
# 9. HEALTH CHECK
# ============================================================================

class TestHealth:
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# ============================================================================
# 10. API DOCS ACCESSIBLE
# ============================================================================

class TestDocs:
    async def test_openapi_json(self, client):
        resp = await client.get("/api/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert "paths" in data
        assert "/api/v1/laws/search" in data["paths"]
        assert "/api/v1/laws/browse" in data["paths"]
        assert "/api/v1/laws/stats" in data["paths"]
        assert "/api/v1/auth/register" in data["paths"]
        assert "/api/v1/auth/login" in data["paths"]
