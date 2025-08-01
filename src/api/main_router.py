from fastapi import APIRouter
from src.api.hello_world.main import router as hello_world_router
from src.api.library import book_api, borrow_api, customer_api


router = APIRouter()

router.include_router(hello_world_router)
router.include_router(book_api.router)
router.include_router(borrow_api.router)
router.include_router(customer_api.router)