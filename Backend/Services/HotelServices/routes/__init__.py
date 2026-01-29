from fastapi import APIRouter

from fastapi import APIRouter

from resources.frontOffice.guestController import router as guestRouter





router = APIRouter()


router.include_router(guestRouter, prefix='', tags=['Guest'])