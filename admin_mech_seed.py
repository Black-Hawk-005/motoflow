import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import select

from app import models
from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.schemas import UserRole


async def main():
    async with AsyncSessionLocal() as db:
        print("\nDefault mechanic credentials:")
        print("email:", "mech202606@motoflow.co.in")
        print("pwd:", "mech@123")
        print("full_name:", "Ryan")
        print("phone:", "12039203232")

        print("\nDefault admin credentials:")
        print("email:", "admin@motoflow.co.in")
        print("pwd:", "admin@123")
        print("full_name:", "admin")
        print("phone:", "234823031214")

        result = await db.execute(
            select(models.User).where(
                models.User.email == "mech202606@motoflow.co.in",
            )
        )
        existing_mechanic = result.scalars().one_or_none()
        if not existing_mechanic:
            default_mechanic = models.User(
                role=UserRole.MECHANIC,
                full_name="Ryan",
                email="mech202606@motoflow.co.in",
                phone="12039203232",
                password_hash=hash_password("mech@123"),
            )
            db.add(default_mechanic)

        result = await db.execute(
            select(models.User).where(
                models.User.email == "admin@motoflow.co.in",
            )
        )
        existing_admin = result.scalars().one_or_none()
        if not existing_admin:
            default_admin = models.User(
                role=UserRole.ADMIN,
                full_name="admin",
                email="admin@motoflow.co.in",
                phone="234823031214",
                password_hash=hash_password("admin@123"),
            )

            db.add(default_admin)
        await db.commit()
        print("Added default mechanic and admin")
        print("done")


asyncio.run(main())
