import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.database import get_db
from app.main import app


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
    )

    database_url: str
    secret_key: SecretStr
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"


test_settings = TestSettings()  # type: ignore [call-arg]


from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

test_engine = create_async_engine(
    test_settings.database_url,
)

AsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://test",
    ) as client:
        yield client
