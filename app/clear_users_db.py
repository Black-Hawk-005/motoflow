import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import delete

from app.database import AsyncSessionLocal
from app.models import Users


async def main():
    async with AsyncSessionLocal() as db:
        await db.execute(delete(Users))
        await db.commit()
        print("done")


asyncio.run(main())
