from fastapi import APIRouter
from controllers.user_controller import router as user_router
from controllers.furniture_controller import router as furniture_router

router = APIRouter()

router.include_router(user_router, prefix="/users", tags=["users"])
router.include_router(furniture_router, prefix="/furnitures", tags=["furnitures"])

