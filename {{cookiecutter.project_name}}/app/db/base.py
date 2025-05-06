from typing import Any, Optional, Sequence, Type, TypeVar

from sqlalchemy import Row, RowMapping, exc, select
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import Select

from app.settings import get_settings

settings = get_settings()

Base = declarative_base()

T = TypeVar('T', bound='DBMixin')


class DBMixin:
    @classmethod
    async def create(cls: Type[T], db: AsyncSession, **kwargs) -> Optional[T]:
        try:
            obj = cls(**kwargs)
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            return obj

        except exc.IntegrityError:
            await db.rollback()
            return None

    @classmethod
    async def get(cls: Type[T], db: AsyncSession, **filters) -> Optional[T]:
        stmt = select(cls).filter_by(**filters)
        result = await db.execute(stmt)
        try:
            return result.scalars().unique().one_or_none()
        except MultipleResultsFound:
            raise

    @classmethod
    async def filter(
        cls: Type[T], db: AsyncSession, **filters
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        stmt = select(cls).filter_by(**filters)
        result = await db.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def all(cls: Type[T], db: AsyncSession) -> Sequence[Row[Any] | RowMapping | Any]:
        stmt = select(cls)
        result = await db.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def query(
        cls: Type[T], db: AsyncSession, stmt: Select
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        result = await db.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def update(cls: Type[T], db: AsyncSession, pk: int, **kwargs) -> Optional[T]:
        obj = await db.get(cls, pk)
        if obj is None:
            return None

        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        await db.commit()
        await db.refresh(obj)
        return obj

    @classmethod
    async def delete(cls, db: AsyncSession, pk: int) -> bool:
        obj = await db.get(cls, pk)
        if obj is None:
            return False

        await db.delete(obj)
        await db.commit()
        return True
