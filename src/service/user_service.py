# src/services/user_service.py
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.service.base_service import BaseService
from src.repository.user_repository import UserRepository
from src.dto.user_dto import UserCreateDTO, UserUpdateDTO, UserDTO
from src.utils.security_utils import get_password_hash, verify_password


class UserService(BaseService[UserCreateDTO, UserUpdateDTO, UserDTO, UserRepository]):
    def __init__(self, repo: Optional[UserRepository] = None):
        super().__init__(repo or UserRepository(), response_model=UserDTO)

    async def create(self, db: AsyncSession, obj_in: UserCreateDTO) -> UserDTO:
        create_data = obj_in.model_dump(exclude_unset=True)
        
        if 'password' in create_data:
            create_data['password_hash'] = get_password_hash(create_data.pop('password'))
        
        create_data.setdefault('is_active', True)
        create_data.setdefault('last_login', datetime.now())
    
        print(f"Final create_data: {create_data}")

        obj = await self.repo.create(db, obj_in=create_data)
        return self._to_dto(obj)

    async def login(self, db: AsyncSession, username: str, password: str) -> Optional[UserDTO]:
        """
        Authenticate a user with username/email and password.
        
        Args:
            db: Database session
            username: Username or email address
            password: Plain text password
            
        Returns:
            UserDTO if authentication successful, None otherwise
        """
        user = await self.repo.get_by_name(db, name=username)
        
        if user is None:
            user = await self.repo.get_by_email(db, email=username)
        
        if user is None or not verify_password(password, user.password_hash) or not user.is_active:
            return None
        
        return self._to_dto(user)

    async def login_with_email(self, db: AsyncSession, email: str, password: str) -> Optional[UserDTO]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: Email address
            password: Plain text password
            
        Returns:
            UserDTO if authentication successful, None otherwise
        """
        user = await self.repo.get_by_email(db, email=email)
        
        if user is None or not verify_password(password, user.password_hash) or not user.is_active:
            return None
        
        return self._to_dto(user)

    async def login_with_username(self, db: AsyncSession, username: str, password: str) -> Optional[UserDTO]:
        """
        Authenticate a user with username and password.
        
        Args:
            db: Database session
            username: Username
            password: Plain text password
            
        Returns:
            UserDTO if authentication successful, None otherwise
        """
        user = await self.repo.get_by_name(db, name=username)
        
        if user is None or not verify_password(password, user.password_hash) or not user.is_active:
            return None
        
        return self._to_dto(user)

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[UserDTO]:
        user = await self.repo.get_by_name(db, name=username)
        return self._to_dto(user)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[UserDTO]:
        user = await self.repo.get_by_email(db, email=email)
        return self._to_dto(user)

    async def get_by_phone(self, db: AsyncSession, phone: str) -> Optional[UserDTO]:
        user = await self.repo.get_by_phone(db, phone=phone)
        return self._to_dto(user)

    async def search_users(
        self,
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserDTO]:
        users = await self.repo.search(db, search_term=search_term, skip=skip, limit=limit)
        return self._to_dto_list(users)