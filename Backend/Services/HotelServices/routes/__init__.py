from fastapi import APIRouter

from fastapi import APIRouter

from resources.frontOffice.housekeepingController import router as housekeepingRouter

router = APIRouter()


router.include_router(housekeepingRouter, prefix='', tags=['Housekeeping'])