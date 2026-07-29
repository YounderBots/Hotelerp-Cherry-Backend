from fastapi import APIRouter

from resources.loginController import router as loginRouter
from resources.tableController import router as tableRouter
from resources.menuController import router as menuRouter
from resources.orderController import router as orderRouter
from resources.kitchenController import router as kitchenRouter
from resources.billingController import router as billingRouter
from resources.inventoryController import router as inventoryRouter
from resources.guestController import router as guestRouter
from resources.staffController import router as staffRouter
from resources.reportsController import router as reportsRouter
from resources.settingsController import router as settingsRouter

router = APIRouter()

router.include_router(loginRouter, prefix='', tags=['Auth & Proxy'])
router.include_router(tableRouter, prefix='', tags=['Table Management'])
router.include_router(menuRouter, prefix='', tags=['Menu Management'])
router.include_router(orderRouter, prefix='', tags=['Order Taking'])
router.include_router(kitchenRouter, prefix='', tags=['Kitchen / KOT'])
router.include_router(billingRouter, prefix='', tags=['Billing'])
router.include_router(inventoryRouter, prefix='', tags=['Inventory'])
router.include_router(guestRouter, prefix='', tags=['Guest Management'])
router.include_router(staffRouter, prefix='', tags=['Staff Management'])
router.include_router(reportsRouter, prefix='', tags=['Reports & Analytics'])
router.include_router(settingsRouter, prefix='', tags=['Settings'])
