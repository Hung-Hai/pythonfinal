from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.users_models import UsersModel
from src.dto.user_dto import UserCreateDTO, UserUpdateDTO, UserDTO
from src.repository.base_repository import BaseRepository

class UserRepository(BaseRepository[UsersModel, UserCreateDTO, UserUpdateDTO, UserDTO]):
    def __init__(self):
        super().__init__(UsersModel)

    def _model_to_dto(self, db_obj: UsersModel) -> UserDTO:
        """Convert SQLAlchemy model to DTO with roles"""
        if not db_obj:
            return None
            
        # Convert roles to both IDs and full objects
        # role_ids = [role.id for role in db_obj.roles] if db_obj.roles else []
        # roles = [{"id": role.id, "name": role.name} for role in db_obj.roles] if db_obj.roles else []
        
        return UserDTO(
            id=db_obj.id,
            username=db_obj.username,
            first_name=db_obj.first_name,
            last_name=db_obj.last_name,
            email=db_obj.email,
            password_hash=db_obj.password_hash,
            address=db_obj.address,
            phone=db_obj.phone,
            is_active=db_obj.is_active,
            last_login=db_obj.last_login,
            # roles=roles,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at
        )
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[UserDTO]:
        query = select(self.model).filter(self.model.id == id)
        query = self._apply_eager_loads(query)
        result = await db.execute(query)
        db_obj = result.scalars().first()
        return self._model_to_dto(db_obj)

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[UserDTO]:
        query = select(self.model).offset(skip).limit(limit)
        query = self._apply_eager_loads(query)
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        result = await db.execute(query)
        db_objs = result.scalars().all()
        return [self._model_to_dto(obj) for obj in db_objs]

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[UserDTO]:
        query = select(self.model).where(self.model.username == name)
        query = self._apply_eager_loads(query)
        result = await db.execute(query)
        db_obj = result.scalars().first()
        return self._model_to_dto(db_obj)

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[UserDTO]:
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()

    async def get_by_phone(self, db: AsyncSession, *, phone: str) -> Optional[UserDTO]:
        result = await db.execute(select(self.model).where(self.model.phone == phone))
        return result.scalars().first()

    async def search(
        self,
        db: AsyncSession,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserDTO]:
        result = await db.execute(
            select(self.model)
            .where(
                self.model.name.ilike(f"%{search_term}%") |
                self.model.email.ilike(f"%{search_term}%") |
                self.model.phone.ilike(f"%{search_term}%")
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()