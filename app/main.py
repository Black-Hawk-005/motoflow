import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.routers import admin, auth, service_line_items, service_requests, vehicles

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
app.include_router(
    service_requests.router, prefix="/service-requests", tags=["service-requests"]
)
app.include_router(service_line_items.router, prefix="/line-items", tags=["line-items"])
