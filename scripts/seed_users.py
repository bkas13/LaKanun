"""
Seed 4 test users (one per role) for UAT.

Usage:
    python -m scripts.seed_users
    python -m scripts.seed_users --reset   # delete all users first
"""

import asyncio
import argparse
from pathlib import Path
import sys

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, text
from backend.database import engine, async_session, Base
from backend.models.user import User, Role
from backend.utils import hash_password

USERS = [
    {
        "email": "public@test.com",
        "name": "Public User",
        "password": "Test1234!",
        "role": Role.PUBLIC,
    },
    {
        "email": "lawyer@test.com",
        "name": "Lawyer Ramesh",
        "password": "Test1234!",
        "role": Role.LAWYER,
    },
    {
        "email": "judge@test.com",
        "name": "Judge Sita",
        "password": "Test1234!",
        "role": Role.JUDGE,
    },
    {
        "email": "admin@test.com",
        "name": "Admin Biswas",
        "password": "Test1234!",
        "role": Role.ADMIN,
    },
]


async def seed(reset: bool = False):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        if reset:
            await db.execute(text("DELETE FROM users"))
            await db.commit()
            print("  All existing users deleted.")

        for u in USERS:
            existing = (await db.execute(select(User).where(User.email == u["email"]))).scalar_one_or_none()
            if existing:
                print(f"  {u['email']} already exists (id={existing.id}), skipping.")
                continue

            user = User(
                email=u["email"],
                name=u["name"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(user)
            await db.flush()
            print(f"  Created {u['email']:25s}  role={u['role'].value:7s}  id={user.id}")

        await db.commit()
        print("\nDone!  Users seeded.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed test users")
    parser.add_argument("--reset", action="store_true", help="Delete all users first")
    args = parser.parse_args()
    asyncio.run(seed(reset=args.reset))
