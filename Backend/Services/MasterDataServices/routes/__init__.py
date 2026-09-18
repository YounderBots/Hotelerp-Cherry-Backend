from fastapi import APIRouter

#==================================>Master Data Start<==================================
from resources.masterController import router as hotelmasterRouter
from resources.snapshotController import router as snapshotRouter
#==================================>Master Data End<==================================

router = APIRouter()

#==================================>Master Data Start<==================================
router.include_router(hotelmasterRouter, prefix='', tags=['Hotel Master Data'])
# What sibling services read from and write back to Master Data over HTTP.
router.include_router(snapshotRouter, prefix='', tags=['Sibling services'])
#==================================>Master Data End<==================================