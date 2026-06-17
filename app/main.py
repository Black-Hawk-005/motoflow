import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.routers import auth

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
