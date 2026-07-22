#!/usr/bin/env bash
set -e

# ─── ल Kanun — One-command launcher ───────────────────────────────────────

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}➜${NC} $1"; }
ok()    { echo -e "${GREEN}✓${NC} $1"; }
fail()  { echo -e "${RED}✗${NC} $1"; exit 1; }

# ── Prerequisites ──────────────────────────────────────────────────────────

info "Checking prerequisites..."

PYTHON=$(command -v python3 || command -v python)
NODE=$(command -v node)
[[ -n "$PYTHON" ]] || fail "Python 3.10+ is required — https://python.org"
[[ -n "$NODE" ]]   || fail "Node.js 18+ is required — https://nodejs.org"

PY_VER=$($PYTHON --version 2>&1)
NODE_VER=$($NODE --version)
ok "$PY_VER"
ok "Node.js $NODE_VER"

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# ── Backend setup ──────────────────────────────────────────────────────────

info "Setting up backend..."

if [ ! -d venv ]; then
    $PYTHON -m venv venv
    ok "Virtual environment created"
fi

source venv/bin/activate

pip install -q --upgrade pip
pip install -q -r requirements.txt 2>&1 | tail -1
pip install -q "bcrypt==4.0.1" "pytest-asyncio==0.24.0"

ok "Backend dependencies installed"

# Seed test users
info "Seeding test users..."
$PYTHON -m scripts.seed_users --reset 2>/dev/null || $PYTHON -m scripts.seed_users
ok "Test users seeded"

# ── Frontend setup ─────────────────────────────────────────────────────────

info "Setting up frontend..."

cd frontend
if [ ! -d node_modules ]; then
    npm install --silent 2>&1 | tail -1
fi

# Ensure no stale tunnel URL
rm -f .env.local

ok "Frontend dependencies installed"
cd "$DIR"

# ── Launch ─────────────────────────────────────────────────────────────────

info "Starting backend on :8000..."
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level warning > /tmp/kanun-backend.log 2>&1 &
BACKEND_PID=$!
sleep 2

# Verify backend started
if curl -s -o /dev/null http://localhost:8000/health; then
    ok "Backend running on http://localhost:8000"
else
    fail "Backend failed to start — check /tmp/kanun-backend.log"
fi

info "Starting frontend on :3030..."
cd frontend
npx next dev --port 3030 > /tmp/kanun-frontend.log 2>&1 &
FRONTEND_PID=$!
cd "$DIR"

sleep 5

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo -e "  ${CYAN}ल Kanun${NC} is running!"
echo ""
echo -e "  Frontend:  ${CYAN}http://localhost:3030${NC}"
echo -e "  Backend:   ${CYAN}http://localhost:8000${NC}"
echo -e "  API docs:  ${CYAN}http://localhost:8000/api/docs${NC}"
echo ""
echo -e "  ${GREEN}Test credentials:${NC}"
echo -e "    👤 Public  → public@test.com / Test1234!"
echo -e "    ⚖️ Lawyer  → lawyer@test.com / Test1234!"
echo -e "    🏛️ Judge   → judge@test.com  / Test1234!"
echo -e "    🔧 Admin   → admin@test.com  / Test1234!"
echo ""
echo -e "  Open ${CYAN}http://localhost:3030${NC} in your browser."
echo -e "  Press ${RED}Ctrl+C${NC} to stop both servers."
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"

# Trap to clean up on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; ok 'Servers stopped.'" EXIT INT TERM

# Wait
wait
