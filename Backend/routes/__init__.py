from fastapi import APIRouter

#==================================>Login Start<==================================
from resources.loginController import router as loginRouter
#==================================>Login End<==================================

#==================================>Dashboard Start<==================================
from resources.dashboardController import router as dashboardRouter
#==================================>Dashboard End<==================================

#==================================>Front Office Start<==================================
from resources.hotel.front_office.guestController import router as hotelguestRouter
from resources.hotel.front_office.reservationController import router as reservationRouter
from resources.hotel.front_office.house_keepingController import router as housekeepingRouter
#========================>Inquiry 
from resources.hotel.front_office.inquiryController import router as inquiryRouter
#==================================>Front Office End<==================================

#==================================>HRM Start<==================================
from resources.hrm.employeeController import router as employeeRouter
#==================================>HRM End<==================================

#==================================>Master Data Start<==================================
from resources.masterdata.masterController import router as hotelmasterRouter
#==================================>Master Data End<==================================

#==================================>House Keeping  Start<==================================
from resources.hotel.front_office.house_keepingController import router as housekeepingRouter
#==================================>House Keeping  End<==================================

#==================================>Night Auditing Start<==================================
from resources.nightauditingController import router as nightauditingRouter
#==================================>Night Auditing End<==================================

#==================================>Restaurant Start<==================================
from resources.restaurant.floor_tableController import router as floorTableRouter
from resources.restaurant.reservationController import router as restaurantReservationRouter
from resources.restaurant.menu_managementController import router as menuManagementRouter
from resources.restaurant.order_managementController import router as orderManagementRouter
from resources.restaurant.kitchenController import router as kitchenRouter
from resources.restaurant.billingController import router as billingRouter
from resources.restaurant.inventoryController import router as inventoryRouter
from resources.restaurant.staffController import router as restaurantStaffRouter
from resources.restaurant.guestController import router as restaurantGuestRouter
from resources.restaurant.reportsController import router as restaurantReportsRouter
#==================================>Restaurant End<==================================

from fastapi.templating import Jinja2Templates


router = APIRouter()

#==================================>Login Start<==================================
router.include_router(loginRouter, prefix='', tags=['Login'])
#==================================>Login End<==================================

#==================================>Dashboard Start<==================================
router.include_router(dashboardRouter, prefix='', tags=['Dashboard'])
#==================================>Dashboard End<==================================

#==================================>Front Office Start<==================================
router.include_router(hotelguestRouter, prefix='', tags=['Hotel Guest'])
router.include_router(reservationRouter,prefix='',tags=['Reservation'])
router.include_router(inquiryRouter,prefix='', tags=['Hotel Inquiry'])
#==================================>Front Office End<==================================

#==================================>HRM Start<==================================
router.include_router(employeeRouter, prefix='', tags=['HRM'])
#==================================>HRM End<==================================

#==================================>Master Data Start<==================================
router.include_router(hotelmasterRouter, prefix='', tags=['Hotel Master Data'])
#==================================>Master Data End<==================================

#==================================>HouseKeeping Start<==================================
router.include_router(housekeepingRouter,prefix='',tags=['Housekeeping'])
#==================================>HouseKeeping End<==================================


#==================================>Night Auditing Start<==================================
router.include_router(nightauditingRouter,prefix='',tags=['Night Auditing'])
#==================================>Night Auditing End<==================================

#==================================>Restaurant Start<==================================
router.include_router(floorTableRouter, prefix='', tags=['Restaurant | Floor & Table'])
router.include_router(restaurantReservationRouter, prefix='', tags=['Restaurant | Reservation'])
router.include_router(menuManagementRouter, prefix='', tags=['Restaurant | Menu'])
router.include_router(orderManagementRouter, prefix='', tags=['Restaurant | Orders'])
router.include_router(kitchenRouter, prefix='', tags=['Restaurant | Kitchen'])
router.include_router(billingRouter, prefix='', tags=['Restaurant | Billing'])
router.include_router(inventoryRouter, prefix='', tags=['Restaurant | Inventory'])
router.include_router(restaurantStaffRouter, prefix='', tags=['Restaurant | Staff'])
router.include_router(restaurantGuestRouter, prefix='', tags=['Restaurant | Guest'])
router.include_router(restaurantReportsRouter, prefix='', tags=['Restaurant | Reports'])
#==================================>Restaurant End<==================================

templates = Jinja2Templates(directory="templates")