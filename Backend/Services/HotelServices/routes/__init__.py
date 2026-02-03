from fastapi import APIRouter
 
from resources.frontOffice.housekeepingController import router as housekeepingRouter
from resources.frontOffice.guestController import router as guestRouter 

router = APIRouter()
 
router.include_router(housekeepingRouter, prefix='', tags=['Housekeeping']) 
router.include_router(guestRouter, prefix='', tags=['Guest']) 