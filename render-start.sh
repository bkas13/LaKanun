#!/usr/bin/env bash
set -e

# Seed test users (safe to run every startup — skips existing)
python -m scripts.seed_users

# Start the API server
exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}" --log-level info
