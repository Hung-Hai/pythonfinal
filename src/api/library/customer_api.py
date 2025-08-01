from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from src.utils.db_utils import create_database_session
from src.dto.customer_dto import CustomerCreateDTO, CustomerUpdateDTO, CustomerDTO
from src.repository.customer_repository import CustomerRepository

router = APIRouter(prefix="/users")

async def get_customer_repo(db: AsyncSession = Depends(create_database_session)) -> CustomerRepository:
    return CustomerRepository()

@router.get("/", response_model=List[CustomerDTO])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000), 
    repo: CustomerRepository = Depends(get_customer_repo),
    db: AsyncSession = Depends(create_database_session)
):
    customers = await repo.get_multi(db, skip=skip, limit=limit)
    if not customers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
    return customers

@router.get("/{customer_id}", response_model=CustomerDTO, summary="Get customer by ID")
async def get_customer(customer_id: UUID,
                   repo: CustomerRepository = Depends(get_customer_repo)):
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="customer not found")
    return customer

@router.get("/searchName/", response_model=List[CustomerDTO],
            summary="Search customers by field")
async def search_customers(value: str = Query(..., description="Insert name"),
                       repo: CustomerRepository = Depends(get_customer_repo),
                       db: AsyncSession = Depends(create_database_session)):
    customers = await repo.get_by_name(db, value)
    if not customers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No customers found with email {value}")
    return customers

@router.post( "/", response_model=CustomerDTO, 
             status_code=status.HTTP_201_CREATED, summary="Create a new customer")
async def create_customer(customer: CustomerCreateDTO,
                      repo: CustomerRepository = Depends(get_customer_repo),
                      db: AsyncSession = Depends(create_database_session)):
    try:
        return await repo.create(db, obj_in=customer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail=str(e))

@router.put("/{customer_id}",response_model=CustomerDTO,
            summary="Update a customer")
async def update_customer(customer_id: UUID, customer_data: CustomerUpdateDTO,
                      repo: CustomerRepository = Depends(get_customer_repo),
                      db: AsyncSession = Depends(create_database_session)):
    customer = await repo.update(db, id=customer_id, obj_in=customer_data)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="customer not found or update failed")
    return customer

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a customer")
async def delete_customer(customer_id: UUID,
                      repo: CustomerRepository = Depends(get_customer_repo),
                      db: AsyncSession = Depends(create_database_session)):
    success = await repo.delete(db, id=customer_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="customer not found or deletion failed")