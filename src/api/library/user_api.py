# src/api/user_api.py
from uuid import UUID
from fastapi import Depends, Query, HTTPException, status, Body
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.library.base_api import BaseAPI
from src.service.user_service import UserService
from src.dto.user_dto import UserDTO, UserCreateDTO, UserUpdateDTO
from src.utils.db_utils import create_database_session
from src.utils.security_utils import create_access_token, verify_password, verify_token  # Import token creation utility
from src.dto.auth_dto import LoginRequest, TokenResponse  # Import auth DTOs


def get_user_service() -> UserService:
    return UserService()


user_api = BaseAPI[UserDTO, UserCreateDTO, UserUpdateDTO, UserService](
    prefix="/users",
    service_provider=get_user_service,
    tags=["Users"],
)
user_api.register_crud_routes()

router = user_api.router

@router.post("/register", response_model=TokenResponse)
async def register(
    register_data: UserCreateDTO = Body(...),
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    """
    Register a new user and return JWT token.
    """
    # Check if user already exists
    existing_user = await service.get_by_username(db, username=register_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    existing_email = await service.get_by_email(db, email=register_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create the user directly - no need to recreate the DTO
    user = await service.create(db, register_data)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest = Body(...),
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    """
    Authenticate user and return JWT token.
    
    Accepts either username or email in the username field.
    """
    user = await service.login(db, username=login_data.username, password=login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.post("/login/email", response_model=TokenResponse)
async def login_with_email(
    login_data: LoginRequest = Body(...),
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    """
    Authenticate user with email and return JWT token.
    """
    user = await service.login_with_email(db, email=login_data.username, password=login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.post("/login/username", response_model=TokenResponse)
async def login_with_username(
    login_data: LoginRequest = Body(...),
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    """
    Authenticate user with username and return JWT token.
    """
    user = await service.login_with_username(db, username=login_data.username, password=login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.get("/search", response_model=List[UserDTO])
async def search_users(
    search: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    users = await service.search_users(db, search_term=search, skip=skip, limit=limit)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching users found")
    return users


@router.get("/by-username/{username}", response_model=UserDTO)
async def get_user_by_username(
    username: str,
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/by-email/{email}", response_model=UserDTO)
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/by-phone/{phone}", response_model=UserDTO)
async def get_user_by_phone(
    phone: str,
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_by_phone(db, phone=phone)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}/password", response_model=UserDTO)
async def update_password(
    user_id: UUID,
    password_data: dict = Body(..., example={"current_password": "oldpass", "new_password": "newpass"}),
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    """
    Update user password with current password verification.
    """
    user = await service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Verify current password
    if not verify_password(password_data["current_password"], user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Update with new password
    update_data = UserUpdateDTO(password=password_data["new_password"])
    updated_user = await service.update(db, user_id, update_data)
    
    return updated_user

@router.put("/{user_id}/profile", response_model=UserDTO)
async def update_profile(
    user_id: UUID,
    profile_data: UserUpdateDTO,
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    """
    Update user profile information (excluding password).
    """
    user = await service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Remove password from update data if present
    update_dict = profile_data.model_dump(exclude_unset=True)
    if 'password' in update_dict:
        del update_dict['password']
    
    updated_user = await service.update(db, user_id, UserUpdateDTO(**update_dict))
    return updated_user

@router.patch("/{user_id}/activate", response_model=UserDTO)
async def activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    """
    Activate a user account.
    """
    user = await service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = UserUpdateDTO(is_active=True)
    updated_user = await service.update(db, user_id, update_data)
    return updated_user


@router.patch("/{user_id}/deactivate", response_model=UserDTO)
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    """
    Deactivate a user account.
    """
    user = await service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = UserUpdateDTO(is_active=False)
    updated_user = await service.update(db, user_id, update_data)
    return updated_user

@router.get("/{user_id}/profile", response_model=UserDTO)
async def get_user_profile(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: UserService = Depends(get_user_service),
):
    """
    Get user profile information by ID.
    """
    user = await service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user