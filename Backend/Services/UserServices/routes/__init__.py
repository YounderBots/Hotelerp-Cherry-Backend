from fastapi import APIRouter

from resources.userController import router as userRouter

router = APIRouter()
router.include_router(userRouter, prefix="", tags=["Users"])
