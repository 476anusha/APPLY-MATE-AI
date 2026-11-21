"""Generic async CRUD repository base class."""
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic async CRUD repository with common operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: UUID) -> ModelType | None:
        """Fetch a single record by primary key."""
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Fetch multiple records with pagination."""
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        """Create a new record from a dict or schema."""
        if hasattr(obj_in, "model_dump"):
            data = obj_in.model_dump(exclude_unset=True)
        else:
            data = dict(obj_in)
        db_obj = self.model(**data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: UUID, obj_in: dict[str, Any] | object) -> ModelType | None:
        """Update a record by id."""
        db_obj = await self.get(id)
        if not db_obj:
            return None
        if hasattr(obj_in, "model_dump"):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = dict(obj_in)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> bool:
        """Delete a record by id. Returns True if deleted."""
        db_obj = await self.get(id)
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def get_by_field(self, field: str, value: Any) -> ModelType | None:
        """Fetch a single record matching field == value."""
        col = getattr(self.model, field, None)
        if col is None:
            raise AttributeError(f"Model {self.model.__name__} has no field '{field}'")
        result = await self.db.execute(select(self.model).where(col == value))
        return result.scalar_one_or_none()

    async def get_multi_by_field(self, field: str, value: Any) -> list[ModelType]:
        """Fetch all records matching field == value."""
        col = getattr(self.model, field, None)
        if col is None:
            raise AttributeError(f"Model {self.model.__name__} has no field '{field}'")
        result = await self.db.execute(select(self.model).where(col == value))
        return list(result.scalars().all())
