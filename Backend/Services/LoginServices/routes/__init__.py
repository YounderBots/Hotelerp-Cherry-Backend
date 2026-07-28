from fastapi import APIRouter

from resources.loginController import router as userRouter

router = APIRouter()
router.include_router(userRouter, prefix="", tags=["Users"])
