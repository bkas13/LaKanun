# UAT — ल Kanun Legal AI Platform

## Quick Start

```bash
# 1. Seed test users (first time or after DB reset)
cd /Users/13pokharel/NepalLawProject/nepal_legal_project
python3 -m scripts.seed_users

# 2. Start backend
uvicorn backend.main:app --reload --port 8000

# 3. Start frontend (separate terminal)
cd frontend && npm run dev   # runs on port 3000
```

---

## Test Credentials

| Role     | Email               | Password   | Can Do                                        |
|----------|----------------------|------------|-----------------------------------------------|
| Public   | `public@test.com`    | `Test1234!`| Search, browse, read laws, rights scenarios   |
| Lawyer   | `lawyer@test.com`    | `Test1234!`| + Bookmarks, notes, case prep                 |
| Judge    | `judge@test.com`     | `Test1234!`| + Annotations, case summaries                 |
| Admin    | `admin@test.com`     | `Test1234!`| + Full admin panel, user mgmt, audit logs     |

> **Registering new users:** Any visitor can register → always creates a **public** role account.  
> Admin/judge/lawyer roles must be assigned via admin panel or by running the seed script with `--reset`.

---

## Useful Info

| Item | Value |
|------|-------|
| Frontend URL | `http://localhost:3000` |
| Backend API | `http://localhost:8000` |
| Swagger docs | `http://localhost:8000/api/docs` |
| SQLite DB | `data/kanun.db` |
| Supported countries | Nepal, India, All |
| Supported locales | English (en), Nepali (ne), Hindi (hi) |
| Corpus size | ~6,656 provisions (Nepal 2,655 + India 4,001) |
| JWT access token | 15 min expiry |
| JWT refresh token | 7 days expiry |
| API prefix | `/api/v1/` |

---

## Test Scenarios

### 1. Public User (unauthenticated)

| # | Action | Expected Result |
|---|--------|-----------------|
| 1.1 | Visit homepage | Hero loads, "Popular Laws" section shows curated provisions |
| 1.2 | Type in search box → type "land rights" | Autocomplete suggestions appear |
| 1.3 | Submit search | Results modal opens with relevance scores |
| 1.4 | Click a result | Detail card shows citation, plain language summary, source URL |
| 1.5 | Switch country to "Nepal" | Search filters to Nepal-only provisions |
| 1.6 | Switch country to "India" | Search filters to India-only provisions |
| 1.7 | Switch locale to NE | Full UI in Nepali |
| 1.8 | Switch locale to HI | Full UI in Hindi |
| 1.9 | Click "Know Your Rights" | 16 scenarios listed |
| 1.10 | Click a scenario | Rights list, obligations, deadlines, where to go shown |
| 1.11 | Click "Know Your Issues" | 19 issue patterns listed |
| 1.12 | Click "Browse Laws" tab | Category tiles with counts, Popular/Recent tabs |
| 1.13 | Click Popular tab | Ranked provisions with view counts |
| 1.14 | Click Recent tab | Recently enacted laws with year badges |
| 1.15 | Click a law → detail page | `/laws/[id]` loads, view count increments |
| 1.16 | Try to bookmark | Redirected to login (requires lawyer+ role) |
| 1.17 | Visit `/faq` | FAQ page loads with all questions |

### 2. Lawyer Role (`lawyer@test.com`)

| # | Action | Expected Result |
|---|--------|-----------------|
| 2.1 | Login | Redirects to `/dashboard` |
| 2.2 | Dashboard | Shows user stats, bookmarks section |
| 2.3 | Search a provision → click Bookmark icon | Bookmarked (yellow star) |
| 2.4 | Go to dashboard → Bookmarks | Bookmarked provision appears in list |
| 2.5 | Unbookmark | Star returns to outline |
| 2.6 | Visit `/laws/[id]` | Bookmark button available on detail page |
| 2.7 | Open search result modal → click "Plain Language" tab | Human-readable summary shown |
| 2.8 | Visit FAQ | Full FAQ content |

### 3. Judge Role (`judge@test.com`)

| # | Action | Expected Result |
|---|--------|-----------------|
| 3.1 | Login | Redirects to `/dashboard` |
| 3.2 | Dashboard | Judge-specific features visible |
| 3.3 | All lawyer features work | Bookmarks, notes, search |

### 4. Admin Role (`admin@test.com`)

| # | Action | Expected Result |
|---|--------|-----------------|
| 4.1 | Login | Redirects to `/dashboard` |
| 4.2 | Dashboard | Admin panel with user list, stats |
| 4.3 | GET `/api/v1/admin/users` | Lists all users |
| 4.4 | GET `/api/v1/admin/users/count` | Returns counts by role |
| 4.5 | GET `/api/v1/admin/stats` | Corpus stats (provisions by country, category) |
| 4.6 | GET `/api/v1/admin/audit` | Audit log entries |
| 4.7 | PATCH `/api/v1/admin/users/{id}` | Update a user's role |

### 5. API Smoke Tests (via Swagger or curl)

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test","password":"Test1234!"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"public@test.com","password":"Test1234!"}'

# Search (public, no auth)
curl "http://localhost:8000/api/v1/laws/search?q=murder&country=nepal"

# Browse laws (public)
curl "http://localhost:8000/api/v1/laws/browse?limit=10"

# Popular laws
curl "http://localhost:8000/api/v1/laws/popular?limit=10"

# Categories
curl "http://localhost:8000/api/v1/laws/categories"

# Recent laws
curl "http://localhost:8000/api/v1/laws/recent?limit=10"

# Track view
curl -X POST http://localhost:8000/api/v1/laws/1/view \
  -H "Authorization: Bearer <access_token>"

# Bookmark (lawyer+)
curl -X POST http://localhost:8000/api/v1/laws/bookmarks \
  -H "Authorization: Bearer <lawyer_token>" \
  -H "Content-Type: application/json" \
  -d '{"provision_id":"1","country":"nepal","title":"Test bookmark"}'

# Rights scenarios
curl "http://localhost:8000/api/v1/rights"

# Issue finder
curl "http://localhost:8000/api/v1/issues/search?q=property+dispute&country=nepal"
```

### 6. Locale & Country Independence

| # | Action | Expected Result |
|---|--------|-----------------|
| 6.1 | Set country=Nepal, locale=EN | Nepal-only results, English UI |
| 6.2 | Set country=India, locale=NE | India-only results, Nepali UI |
| 6.3 | Set country=All, locale=HI | All results, Hindi UI |
| 6.4 | Refresh page | Both preferences persist (localStorage) |

### 7. Cross-Browser / Mobile

| # | Action | Expected Result |
|---|--------|-----------------|
| 7.1 | Resize to mobile (<768px) | Bottom tab bar appears (Home, Laws, Rights, Issues, More) |
| 7.2 | Tap "More" | Slide-up drawer with switchers + auth |
| 7.3 | Desktop (>768px) | Slim header with nav items |
| 7.4 | Language switcher | Works in both mobile drawer and desktop header |

---

## Re-seeding

```bash
# Wipe and recreate all 4 test users
python3 -m scripts.seed_users --reset
```
