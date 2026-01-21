from fastapi import APIRouter

#==================================>Master Data Start<==================================
from resources.masterdata.masterController import router as hotelmasterRouter
#==================================>Master Data End<==================================

router = APIRouter()

#==================================>Master Data Start<==================================
router.include_router(hotelmasterRouter, prefix='', tags=['Hotel Master Data'])
#==================================>Master Data End<==================================