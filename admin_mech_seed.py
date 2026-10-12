import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import select

from app import models
from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.schemas import UserRole


class SeedSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    seed_admin_email: str
    seed_admin_password: SecretStr
    seed_mechanic_email: str
    seed_mechanic_password: SecretStr


async def main():
    seed_settings = SeedSettings()  # type: ignore [call-arg]

    async with AsyncSessionLocal() as db:
        admin_email = seed_settings.seed_admin_email
        admin_password = seed_settings.seed_admin_password.get_secret_value()
        mech_email = seed_settings.seed_mechanic_email
        mech_password = seed_settings.seed_mechanic_password.get_secret_value()

        print("\nDefault mechanic details:")
        print("full_name:", "Ryan")
        print("phone:", "12039203232")

        print("\nDefault admin details:")
        print("full_name:", "admin")
        print("phone:", "234823031214")

        result = await db.execute(
            select(models.User).where(
                models.User.email == mech_email,
            )
        )
        existing_mechanic = result.scalars().one_or_none()
        if not existing_mechanic:
            default_mechanic = models.User(
                role=UserRole.MECHANIC,
                full_name="Ryan",
                email=mech_email,
                phone="12039203232",
                password_hash=hash_password(mech_password),
            )
            db.add(default_mechanic)

        result = await db.execute(
            select(models.User).where(
                models.User.email == admin_email,
            )
        )
        existing_admin = result.scalars().one_or_none()
        if not existing_admin:
            default_admin = models.User(
                role=UserRole.ADMIN,
                full_name="admin",
                email=admin_email,
                phone="234823031214",
                password_hash=hash_password(admin_password),
            )

            db.add(default_admin)
        await db.commit()
        print("Added default mechanic and admin")
        print("done")


if __name__ == "__main__":
    asyncio.run(main())
