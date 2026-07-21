import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.routers import (
    admin,
    auth,
    comments,
    service_line_items,
    service_requests,
    vehicles,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # shutdown
    await engine.dispose()


origins = [
    "http://localhost:5173",  # Default Vite port
    "http://127.0.0.1:5173",
]

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
app.include_router(
    service_requests.router, prefix="/service-requests", tags=["service-requests"]
)
app.include_router(service_line_items.router, prefix="/line-items", tags=["line-items"])
app.include_router(comments.router, prefix="/comments", tags=["comments"])
