from sqlalchemy import Integer, TIMESTAMP, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declared_attr, declarative_base, sessionmaker, \
    mapped_column

from app.core.config import settings


class PreBase:
    """Абстрактная модель для наследования"""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = mapped_column(Integer, primary_key=True)
    created_at = mapped_column(TIMESTAMP,
                               server_default=func.current_timestamp(),
                               nullable=False)
    updated_at = mapped_column(TIMESTAMP,
                               server_default=func.current_timestamp(),
                               nullable=False,
                               onupdate=func.current_timestamp())


Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.DATABASE_URL)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    """Генератор асинхронной сессии"""
    async with AsyncSessionLocal() as async_session_gen:
        yield async_session_gen
