# src/repositories/base.py
from typing import Type, TypeVar, Generic, Optional, List, Any, Dict
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType, SchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.eager_loads = getattr(model, '__eager_loads__', [])

    def _apply_eager_loads(self, query):
        """Apply eager loading options to query"""
        for relationship in self.eager_loads:
            query = query.options(selectinload(getattr(self.model, relationship)))
        return query

    async def get(self, db: AsyncSession, id: UUID) -> Optional[SchemaType]:
        query = select(self.model).filter(self.model.id == id)
        query = self._apply_eager_loads(query)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SchemaType]:
        query = select(self.model).offset(skip).limit(limit)
        query = self._apply_eager_loads(query)
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all(
        self,
        db: AsyncSession,
        *,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SchemaType]:
        query = select(self.model)
        query = self._apply_eager_loads(query)
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: Any) -> ModelType:
        # FIX: Handle both dict and Pydantic model inputs
        if hasattr(obj_in, 'model_dump'):
            # It's a Pydantic model (v2)
            obj_data = obj_in.model_dump(exclude_unset=True)
        elif hasattr(obj_in, 'dict'):
            # It's a Pydantic model (v1)
            obj_data = obj_in.dict(exclude_unset=True)
        else:
            # It's already a dictionary
            obj_data = obj_in
            
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, 
        db: AsyncSession,
        *, 
        id: UUID, 
        obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> Optional[SchemaType]:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        db_obj = result.scalars().first()
        if not db_obj:
            return None
            
        obj_data = obj_in.dict(exclude_unset=True) if isinstance(obj_in, BaseModel) else obj_in
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: UUID) -> bool:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        db_obj = result.scalars().first()
        if not db_obj:
            return False
            
        await db.delete(db_obj)
        await db.commit()
        return True