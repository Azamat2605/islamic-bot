#!/usr/bin/env python3
"""
Diagnostic script to detect and fix duplicate Settings rows.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import AsyncSessionLocal
from database.models import Settings, User


async def find_duplicates() -> list[tuple[int, int]]:
    """Find user_ids with multiple Settings rows."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Settings.user_id, func.count(Settings.id).label("cnt"))
            .group_by(Settings.user_id)
            .having(func.count(Settings.id) > 1)
        )
        result = await session.execute(stmt)
        duplicates = result.all()
        return duplicates


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    """Get User by telegram_id."""
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def inspect_user(user_id: int):
    """Print all Settings rows for a given user_id."""
    async with AsyncSessionLocal() as session:
        stmt = select(Settings).where(Settings.user_id == user_id).order_by(Settings.id)
        result = await session.execute(stmt)
        rows = result.scalars().all()
        print(f"User {user_id} has {len(rows)} Settings rows:")
        for row in rows:
            print(f"  id={row.id}, language={row.language}, updated_at={row.updated_at}")


async def delete_duplicates():
    """Delete duplicate Settings rows, keeping the most recently updated."""
    async with AsyncSessionLocal() as session:
        # Find duplicates
        duplicates = await find_duplicates()
        if not duplicates:
            print("No duplicates found.")
            return
        
        total_deleted = 0
        for user_id, cnt in duplicates:
            print(f"\nProcessing user_id={user_id} with {cnt} rows")
            # Get all rows for this user, ordered by updated_at descending (newest first)
            stmt = (
                select(Settings.id, Settings.updated_at, Settings.language)
                .where(Settings.user_id == user_id)
                .order_by(Settings.updated_at.desc())
            )
            result = await session.execute(stmt)
            rows = result.all()
            # Keep the first row (most recent updated_at)
            keep_id = rows[0].id
            delete_ids = [row.id for row in rows[1:]]
            if delete_ids:
                await session.execute(delete(Settings).where(Settings.id.in_(delete_ids)))
                total_deleted += len(delete_ids)
                print(f"  Kept row id={keep_id} (language={rows[0].language})")
                print(f"  Deleted rows ids={delete_ids}")
        
        await session.commit()
        print(f"\nTotal deleted duplicate rows: {total_deleted}")


async def main():
    print("=== Settings Duplicates Diagnostic ===")
    
    # 1. Check for any duplicates
    duplicates = await find_duplicates()
    if duplicates:
        print(f"Found {len(duplicates)} users with duplicate Settings rows:")
        for user_id, cnt in duplicates:
            print(f"  user_id={user_id}, rows={cnt}")
    else:
        print("No duplicates found.")
    
    # 2. Inspect specific user (telegram_id=8215908853)
    telegram_id = 8215908853
    user = await get_user_by_telegram_id(telegram_id)
    if user:
        print(f"\nInspecting user with telegram_id={telegram_id} (user_id={user.id}):")
        await inspect_user(user.id)
    else:
        print(f"\nUser with telegram_id={telegram_id} not found.")
    
    # 3. Delete duplicates (if any) - automatically delete
    if duplicates:
        print("\nAutomatically deleting duplicates...")
        await delete_duplicates()
    else:
        print("\nNo duplicates to delete.")
    
    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
