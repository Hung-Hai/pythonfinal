from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.customers_models import CustomersModel
from src.dto.customer_dto import CustomerCreateDTO, CustomerUpdateDTO, CustomerDTO
from src.repository.base_repository import BaseRepository

class CustomerRepository(BaseRepository[CustomersModel, CustomerCreateDTO, CustomerUpdateDTO, CustomerDTO]):
    def __init__(self):
        super().__init__(CustomersModel)

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[CustomerDTO]:
        result = await db.execute(select(self.model).where(self.model.name == name))
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[CustomerDTO]:
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()

    async def get_by_phone(self, db: AsyncSession, *, phone: str) -> Optional[CustomerDTO]:
        result = await db.execute(select(self.model).where(self.model.phone == phone))
        return result.scalars().first()

    async def search(
        self,
        db: AsyncSession,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CustomerDTO]:
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