"""Tests for auth, RBAC, and the new backend API."""

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
    """Fresh in-memory DB session per test."""
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
    """Async test client with DB override."""
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


# ── Helper ─────────────────────────────────────────────────────────────

async def create_test_user(db: AsyncSession, email: str, role: Role = Role.PUBLIC, password: str = "testpass123"):
    user = User(
        email=email,
        name=f"Test User {email}",
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login(client: AsyncClient, email: str, password: str = "testpass123") -> dict:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()


# ============================================================================
# Auth Tests
# ============================================================================

class TestAuth:
    async def test_register_success(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "new@test.com", "name": "New User", "password": "securepass123"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["role"] == "public"
        assert data["user"]["email"] == "new@test.com"

    async def test_register_duplicate_email(self, client, db):
        await create_test_user(db, "dup@test.com")
        resp = await client.post("/api/v1/auth/register", json={
            "email": "dup@test.com", "name": "Dup", "password": "securepass123"
        })
        assert resp.status_code == 409

    async def test_register_short_password(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "short@test.com", "name": "Short", "password": "123"
        })
        assert resp.status_code == 422

    async def test_login_success(self, client, db):
        await create_test_user(db, "login@test.com")
        data = await login(client, "login@test.com")
        assert "access_token" in data
        assert data["user"]["email"] == "login@test.com"

    async def test_login_wrong_password(self, client, db):
        await create_test_user(db, "wrong@test.com")
        resp = await client.post("/api/v1/auth/login", json={
            "email": "wrong@test.com", "password": "badpassword"
        })
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "ghost@test.com", "password": "whatever"
        })
        assert resp.status_code == 401

    async def test_me_with_token(self, client, db):
        await create_test_user(db, "me@test.com")
        tokens = await login(client, "me@test.com")
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == "me@test.com"

    async def test_me_without_token(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 403)

    async def test_me_invalid_token(self, client):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401


# ============================================================================
# RBAC Tests
# ============================================================================

class TestRBAC:
    async def test_public_cannot_access_bookmarks(self, client, db):
        user = await create_test_user(db, "pub@test.com", Role.PUBLIC)
        tokens = await login(client, "pub@test.com")
        resp = await client.get(
            "/api/v1/saved/bookmarks",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 403

    async def test_lawyer_can_access_bookmarks(self, client, db):
        user = await create_test_user(db, "law@test.com", Role.LAWYER)
        tokens = await login(client, "law@test.com")
        resp = await client.get(
            "/api/v1/saved/bookmarks",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 200

    async def test_public_cannot_access_admin(self, client, db):
        user = await create_test_user(db, "pub2@test.com", Role.PUBLIC)
        tokens = await login(client, "pub2@test.com")
        resp = await client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 403

    async def test_admin_can_access_admin(self, client, db):
        user = await create_test_user(db, "adm@test.com", Role.ADMIN)
        tokens = await login(client, "adm@test.com")
        resp = await client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 200

    async def test_lawyer_can_create_bookmark(self, client, db):
        user = await create_test_user(db, "lb@test.com", Role.LAWYER)
        tokens = await login(client, "lb@test.com")
        resp = await client.post(
            "/api/v1/saved/bookmarks",
            json={"provision_id": "test_1", "country": "nepal", "title": "Test"},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 201

    async def test_lawyer_can_create_note(self, client, db):
        user = await create_test_user(db, "ln@test.com", Role.LAWYER)
        tokens = await login(client, "ln@test.com")
        resp = await client.post(
            "/api/v1/saved/notes",
            json={"title": "My Case", "content": "Details here"},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 201

    async def test_admin_can_update_user_role(self, client, db):
        admin = await create_test_user(db, "adm2@test.com", Role.ADMIN)
        target = await create_test_user(db, "target@test.com", Role.PUBLIC)
        admin_tokens = await login(client, "adm2@test.com")
        resp = await client.patch(
            f"/api/v1/admin/users/{target.id}",
            json={"role": "lawyer"},
            headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "lawyer"


# ============================================================================
# Law Search Tests
# ============================================================================

class TestLaws:
    async def test_search_returns_results(self, client, db):
        await create_test_user(db, "search@test.com")
        tokens = await login(client, "search@test.com")
        resp = await client.get(
            "/api/v1/laws/search?q=murder&top_k=5",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0

    async def test_search_without_auth(self, client):
        """Laws search is public — no auth required."""
        resp = await client.get("/api/v1/laws/search?q=freedom&top_k=3")
        assert resp.status_code == 200

    async def test_browse(self, client, db):
        await create_test_user(db, "browse@test.com")
        tokens = await login(client, "browse@test.com")
        resp = await client.get(
            "/api/v1/laws/browse?country=nepal&limit=5",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["articles"]) <= 5
