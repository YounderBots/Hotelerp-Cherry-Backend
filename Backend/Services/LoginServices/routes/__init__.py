from fastapi import APIRouter
from sympy import use

#==================================>Master Data Start<==================================
from resources.loginController import router as userRouter
#==================================>Master Data End<==================================

router = APIRouter()

#==================================>Master Data Start<==================================
router.include_router(userRouter, prefix='', tags=['Users'])
#==================================>Master Data End<==================================