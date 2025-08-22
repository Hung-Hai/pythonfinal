from fastapi import APIRouter
from src.api.hello_world.main import router as hello_world_router
from src.api.library import (book_api, loan_api, user_api, author_api, 
                             book_digital_api, book_physical_api, category_api, 
                             publisher_api, rating_api, reservation_api,role_api)


router = APIRouter()

router.include_router(hello_world_router)
router.include_router(book_api.router)
router.include_router(loan_api.router)
router.include_router(user_api.router)
router.include_router(author_api.router)
router.include_router(book_digital_api.router)
router.include_router(book_physical_api.router)
router.include_router(category_api.router)
router.include_router(publisher_api.router)
router.include_router(rating_api.router)
router.include_router(reservation_api.router)
router.include_router(role_api.router)