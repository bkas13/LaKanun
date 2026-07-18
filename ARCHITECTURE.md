# ल Kanun — Architecture Plan

## Current State
- FastAPI backend with basic endpoints (src/api.py)
- Streamlit UI (app_local.py) — unstable as background process
- Self-contained HTML (app.html) — no auth, no roles, no scale
- 6,200+ legal provisions across 28 documents (Nepal + India)
- ChromaDB vector store, sentence-transformers embeddings

## Target Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Next.js Frontend                   │
│  (React, Tailwind, App Router, JWT auth context)     │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │  Public   │ │  Lawyer  │ │  Judge   │ │ Admin  │ │
│  │ Dashboard │ │Dashboard │ │Dashboard │ │Dashboard│ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────┴──────────────────────────────┐
│                  FastAPI Backend                      │
│  /api/v1/                                            │
│  ├── auth/        (register, login, refresh, me)     │
│  ├── users/       (profile, preferences, CRUD)       │
│  ├── laws/        (search, browse, detail)            │
│  ├── saved/       (bookmarks, notes, cases)           │
│  ├── admin/       (users, corpus, analytics)          │
│  └── health       (status, stats)                     │
│                                                      │
│  Middleware:                                          │
│  ├── JWT Authentication                              │
│  ├── Role-Based Access Control (RBAC)                │
│  ├── CORS (origin-restricted)                        │
│  ├── Rate Limiting (slowapi)                         │
│  ├── Request Logging (structlog)                     │
│  └── Error Handling                                  │
│                                                      │
│  Services:                                           │
│  ├── AuthService    (JWT, password hashing, roles)   │
│  ├── UserService    (CRUD, preferences)              │
│  ├── LawService     (search, filter, corpus)         │
│  ├── SavedService   (bookmarks, notes, cases)        │
│  └── AdminService   (analytics, user mgmt)           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│              SQLite (dev) / PostgreSQL (prod)         │
│  Tables:                                             │
│  ├── users (id, email, name, role, hashed_password)  │
│  ├── saved_bookmarks (user_id, provision_id, note)   │
│  ├── case_notes (user_id, title, content, tags)      │
│  ├── search_history (user_id, query, timestamp)      │
│  └── audit_log (user_id, action, target, timestamp)  │
└──────────────────────────────────────────────────────┘
```

## User Roles & Permissions

| Feature | Public | Lawyer | Judge | Admin |
|---------|--------|--------|-------|-------|
| Search laws | ✅ | ✅ | ✅ | ✅ |
| Browse corpus | ✅ | ✅ | ✅ | ✅ |
| View guides/templates | ✅ | ✅ | ✅ | ✅ |
| Save bookmarks | ❌ | ✅ | ✅ | ✅ |
| Create case notes | ❌ | ✅ | ✅ | ✅ |
| Annotate provisions | ❌ | ❌ | ✅ | ✅ |
| Export case summaries | ❌ | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ❌ | ✅ |
| Manage corpus | ❌ | ❌ | ❌ | ✅ |
| View analytics | ❌ | ❌ | ❌ | ✅ |
| System settings | ❌ | ❌ | ❌ | ✅ |

## Project Structure

```
nepal_legal_project/
├── backend/
│   ├── main.py                  # FastAPI app factory
│   ├── config.py                # Settings (pydantic-settings)
│   ├── database.py              # SQLAlchemy engine, session, Base
│   ├── dependencies.py          # FastAPI deps (get_db, get_current_user)
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── bookmark.py
│   │   ├── case_note.py
│   │   └── audit.py
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── law.py
│   │   ├── bookmark.py
│   │   └── case_note.py
│   ├── routers/                 # API route modules
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── laws.py
│   │   ├── saved.py
│   │   └── admin.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── law.py
│   │   └── saved.py
│   ├── middleware/               # Custom middleware
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── errors.py
│   └── utils/                   # Helpers
│       ├── __init__.py
│       ├── security.py          # JWT encode/decode, password hashing
│       └── search.py            # Synonym expansion, fuzzy search
├── frontend/                    # Next.js app (separate repo later)
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── app/                 # App Router pages
│   │   │   ├── layout.tsx       # Root layout with auth provider
│   │   │   ├── page.tsx         # Landing / public search
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx     # Role-based redirect
│   │   │   │   ├── lawyer/page.tsx
│   │   │   │   ├── judge/page.tsx
│   │   │   │   └── admin/page.tsx
│   │   │   ├── laws/
│   │   │   │   ├── page.tsx     # Browse/search laws
│   │   │   │   └── [id]/page.tsx # Law detail
│   │   │   ├── guides/page.tsx
│   │   │   └── reference/page.tsx
│   │   ├── components/
│   │   │   ├── ui/              # Reusable UI (Button, Card, Input)
│   │   │   ├── layout/          # Sidebar, Header, Footer
│   │   │   ├── search/          # SearchBar, SearchResults
│   │   │   ├── law/             # LawCard, LawDetail, FilterBar
│   │   │   └── dashboard/       # Dashboard-specific components
│   │   ├── lib/
│   │   │   ├── api.ts           # API client (fetch wrapper)
│   │   │   ├── auth.ts          # JWT token management
│   │   │   └── i18n.ts          # Translation helpers
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useSearch.ts
│   │   └── contexts/
│   │       └── AuthContext.tsx
│   └── public/
├── src/                         # Keep existing ML/NLP modules
│   ├── embeddings.py
│   ├── classifier.py
│   ├── legal_dictionary.py
│   └── ...
├── data/                        # Keep existing data pipeline
├── tests/
│   ├── test_api.py
│   ├── test_auth.py
│   ├── test_laws.py
│   └── test_app.py              # Keep existing
├── alembic/                     # Database migrations
│   ├── alembic.ini
│   └── versions/
├── requirements.txt
├── pyproject.toml
└── .env.example
```

## Implementation Phases

### Phase 1: Backend Foundation (build first)
1. Create `backend/` package with proper structure
2. Set up SQLAlchemy + SQLite database layer
3. Create User model with role enum (public/lawyer/judge/admin)
4. Implement JWT auth (register, login, refresh, me)
5. Add RBAC middleware/dependencies
6. Refactor existing API endpoints into `backend/routers/laws.py`
7. Add CORS, rate limiting, request logging middleware
8. Create `.env.example` with all required vars
9. Write tests for auth + RBAC

### Phase 2: Saved Features (lawyer + judge)
1. Bookmark model + CRUD API
2. Case notes model + CRUD API
3. Search history tracking
4. Frontend: dashboard layouts per role

### Phase 3: Next.js Frontend
1. Scaffold Next.js with Tailwind
2. Auth pages (login, register)
3. AuthContext with JWT token management
4. Public search page (mirrors current app.html UX)
5. Role-based dashboard routing
6. Lawyer dashboard (bookmarks, notes, case prep)
7. Judge dashboard (annotations, case summaries)
8. Admin dashboard (user management, analytics, corpus mgmt)
9. i18n support (English, Nepali, Hindi)

### Phase 4: Admin & Polish
1. Admin: user CRUD, role assignment
2. Admin: corpus management (add/remove laws)
3. Admin: analytics dashboard
4. Audit logging
5. Production config (PostgreSQL, Docker)
6. Deployment setup

## Key Technical Decisions

- **Auth**: JWT access tokens (15min) + refresh tokens (7 days), bcrypt password hashing
- **RBAC**: Decorator-based `@require_role(Role.LAWYER)` on route handlers
- **Database**: SQLAlchemy async with aiosqlite for dev, asyncpg for prod
- **Frontend**: Next.js 14 App Router, Tailwind CSS, Zustand for state
- **API versioning**: `/api/v1/` prefix
- **Search**: Keep existing keyword search + synonym expansion, add vector search via ChromaDB
- **i18n**: Next.js middleware + next-intl for frontend, pydantic i18n for API messages
