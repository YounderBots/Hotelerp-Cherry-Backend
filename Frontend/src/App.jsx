import React, { useState, useRef, useEffect, Suspense, lazy } from 'react';
import { Search, Bell, Menu, ChevronDown, ChevronRight } from 'lucide-react';
import './App.css'
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Outlet } from 'react-router-dom';
import paLogo from './assets/layout/Cherry.png';
import useClickOutside from './hooks/useClickOutside';
import findMenuByPath from './functions/locationFunctions';
import { getMenuList, ICON_MAP, MENU } from './Sidemenu';
import LogoLoaderComponent from './Authentication/Pages/LogoLoaderComponent';
import ViewFloor from './Restaurant/Floor & Table Setup/FloorPageView';
import ReservationModelView from './Hotel/Reservation/ReservationModelView';
import ReservationListEdit from './Hotel/Reservation/ReservationListEdit';

// Lazy load all page components
const ForgotPassword = lazy(() => import('./Authentication/Pages/ForgotPassword'));
const LockScreen = lazy(() => import('./Authentication/Pages/LockScreen'));
const Login = lazy(() => import('./Authentication/Pages/Login'));
const OTP = lazy(() => import('./Authentication/Pages/OTP'));
const Register = lazy(() => import('./Authentication/Pages/Register'));

// Hotel Components - Lazy loaded with grouping
const AdminDashboard = lazy(() => import('./Hotel/Dashboard/AdminDashboard'));
const Reservation = lazy(() => import('./Hotel/Reservation/Reservation'));
const AddNewReservation = lazy(() => import('./Hotel/Reservation/AddNewReservation'));
const Booking = lazy(() => import('./Hotel/Reservation/Booking'));
const RoomView = lazy(() => import('./Hotel/Reservation/RoomView'));
const ReservationView = lazy(() => import('./Hotel/Reservation/ReservationView'));
const UserReserved = lazy(() => import('./Hotel/Night Audit/UserReserved'));
const RoomBooked = lazy(() => import('./Hotel/Night Audit/RoomBooked'));
const SettlementSummary = lazy(() => import('./Hotel/Night Audit/SettlementSummary'));
const GuestEnquiry = lazy(() => import('./Hotel/Guest Enquiry/GuestEnquiry'));
const Employee = lazy(() => import('./Hotel/HRM/Employee'));
const TaskAssign = lazy(() => import('./Hotel/House Keeper/TaskAssign'));
const RoomIncidentLog = lazy(() => import('./Hotel/House Keeper/RoomIncidentLog'));

// Restaurant Components - Lazy loaded with grouping
const FloorLayout = lazy(() => import('./Restaurant/Floor & Table Setup/FloorLayout'));
const TableMaster = lazy(() => import('./Restaurant/Floor & Table Setup/TableMaster'));
const Orders = lazy(() => import('./Restaurant/Order Management/Orders'));
const TableReservation = lazy(() => import('./Restaurant/Table Reservation/TableReservation'));
const MenuManagement = lazy(() => import('./Restaurant/Menu Management/MenuManagement'));
const MainKitchen = lazy(() => import('./Restaurant/Kitchen Orders/MainKitchen'));
const Grill = lazy(() => import('./Restaurant/Kitchen Orders/Grill'));
const Dessert = lazy(() => import('./Restaurant/Kitchen Orders/Dessert'));
const Bar = lazy(() => import('./Restaurant/Kitchen Orders/Bar'));
const BillingPayments = lazy(() => import('./Restaurant/Billing & Payments/BillingPayments'));
const Stock = lazy(() => import('./Restaurant/Inventory/Stock'));
const ReceipeManagement = lazy(() => import('./Restaurant/Inventory/ReceipeManagement'));
const StaffMaster = lazy(() => import('./Restaurant/Staff Management/StaffMaster'));
const StaffPlanning = lazy(() => import('./Restaurant/Staff Management/StaffPlanning'));
const GuestManagement = lazy(() => import('./Restaurant/Guest Management/GuestManagement'));
const ReportAnalytics = lazy(() => import('./Restaurant/Report & Analytics/ReportAnalytics'));

// Master Data Components - Lazy loaded with grouping
const Facilities = lazy(() => import('./MasterData/Facilities'));
const RoomType = lazy(() => import('./MasterData/RoomType'));
const BedType = lazy(() => import('./MasterData/BedType'));
const HallFloor = lazy(() => import('./MasterData/HallFloor'));
const Rooms = lazy(() => import('./MasterData/Rooms'));
const DiscountType = lazy(() => import('./MasterData/DiscountType'));
const TaxTypes = lazy(() => import('./MasterData/TaxTypes'));
const PaymentMethods = lazy(() => import('./MasterData/PaymentMethods'));
const IdentificationProof = lazy(() => import('./MasterData/IdentificationProof'));
const CurrencyCountry = lazy(() => import('./MasterData/CurrencyCountry'));
const HskTaskType = lazy(() => import('./MasterData/HskTaskType'));
const Complementary = lazy(() => import('./MasterData/Complementary'));
const ReservationStatus = lazy(() => import('./MasterData/ReservationStatus'));
const Department = lazy(() => import('./MasterData/Department'));
const Designation = lazy(() => import('./MasterData/Designation'));

// Error Boundary Component (optional but recommended)
const ErrorBoundaryFallback = () => (
  <div className="error-boundary">
    <h2>Something went wrong while loading this page.</h2>
    <button onClick={() => window.location.reload()}>Reload Page</button>
  </div>
);

// Loading wrapper for lazy components
const PageLoader = ({ children }) => {
  return (
    <Suspense fallback={<LogoLoaderComponent />}>
      {children}
    </Suspense>
  );
};

const Navbar = ({ isMobileMenuOpen, setIsMobileMenuOpen }) => {
  const [profileOpen, setProfileOpen] = useState(false);
  const navigate = useNavigate(); 
  return (
    <nav className="navbar">
      {/* LEFT */}
      <div className="navbar-left">
        <div className="logo-container">
          <img src={paLogo} alt="Cherry" />
        </div>
      </div>

      {/* RIGHT */}
      <div className="navbar-right">
        {/* SEARCH (near notification) */}
        <div className="search-container">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search anything"
          />
        </div>

        {/* NOTIFICATION */}
        <button className="icon-button" title="Notifications">
          <Bell size={18} />
          <span className="notify-dot"></span>
        </button>

        {/* PROFILE */}
        <div className="profile-container">
        <div
          className="profile-box"
          onClick={() => setProfileOpen(prev => !prev)}
        >
          <img
            src="https://images.unsplash.com/photo-1603415526960-f7e0328c63b1?w=80"
            alt="user"
            className="profile-avatar"
          />
          <div className="profile-info">
            <span className="profile-name">Johan Abraham</span>
            <span className="profile-role">Senior Staff</span>
          </div>
          <ChevronDown size={16} />
        </div>

        {profileOpen && (
          <div className="profile-dropdown">
            <div className="dropdown-item">Profile</div>
            <div className="dropdown-item logout"
            onClick={() => {
              navigate("/");
              setProfileOpen(false);
            }}>
              Logout</div>
          </div>
        )}
      </div>



        {/* MOBILE MENU */}
        <button
          className="icon-button mobile-only"
          onClick={() => setIsMobileMenuOpen(prev => !prev)}
        >
          <Menu size={22} />
        </button>
      </div>
    </nav>
  );
};

const RecursiveMenu = ({ items, activePath, setActivePath, level = 0 }) => {
  const navigate = useNavigate();
  
  return (
    <>
      {items.map((item, index) => {
        const pathKey = [...activePath.slice(0, level), index];
        const isActive =
          JSON.stringify(activePath.slice(0, level + 1)) ===
          JSON.stringify(pathKey);
        const hasChildren = item.children?.length;
        const isExpanded = activePath[level] === index;
        
        return (
          <div key={`${item.label}-${level}-${index}`}>
            <div
              className={`sub-item ${isActive ? "active" : ""}`}
              style={{ paddingLeft: `${16 + level * 16}px` }}
              onClick={() => {
                setActivePath(pathKey);
                if (!item.children || item.children.length === 0) {
                  navigate(item.path);
                }
              }}
            >
              {hasChildren && (
                <span className="submenu-arrow">
                  {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </span>
              )}
              {item.label}
            </div>
            {hasChildren && isExpanded && (
              <RecursiveMenu
                items={item.children}
                activePath={activePath}
                setActivePath={setActivePath}
                level={level + 1}
              />
            )}
          </div>
        );
      })}
    </>
  );
};

const AppContext = ({ 
  menuList, 
  activeMenu, 
  setActiveMenu, 
  activePath, 
  setActivePath, 
  children 
}) => {
  const navigate = useNavigate();
  
  return (
    <div className="app-body">
      <aside className="side-nav">
        {menuList.map((item) => {
          const Icon = ICON_MAP[item.id];
          const isActive = item.id === activeMenu?.id;
          
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => {
                setActiveMenu(item);
                if(item.path === undefined) {
                  return navigate(item.children[0].path);
                } 
                navigate(item.path);
              }}
            >
              {Icon && <Icon size={22} />}
              <span>{item.label}</span>
            </div>
          );
        })}
      </aside>
      <div className="content-area">
        {Array.isArray(activeMenu?.children) &&
          activeMenu.children.length > 0 && (
            <div className="sub-menu">
              <RecursiveMenu
                items={activeMenu.children}
                activePath={activePath}
                setActivePath={setActivePath}
              />
            </div>
          )}
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
};

const AppLayout = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [menuList, setMenuList] = useState(MENU);
  const [activeMenu, setActiveMenu] = useState(null);
  const [activePath, setActivePath] = useState([0]);
  const sidebarOutsideRef = useRef(null);
  const location = useLocation();

  useClickOutside(
    sidebarOutsideRef,
    () => setIsMobileMenuOpen(false),
    isMobileMenuOpen
  );
  
  useEffect(() => {
    getMenuList().then(data => {
      console.log("MENU API RESPONSE:", data);
      setMenuList(data.message? data.message : data);
    });
  }, []);

  useEffect(() => {
    if (!menuList.length) return;

    const result = findMenuByPath(menuList, location.pathname);
    if (result) {
      setActiveMenu(result.activeMenu);
      setActivePath(result.activePath);
    }
  }, [location.pathname, menuList]);

  return (
    <>
      <Navbar 
        sidebarOutsideRef={sidebarOutsideRef} 
        setIsMobileMenuOpen={setIsMobileMenuOpen} 
        isMobileMenuOpen={isMobileMenuOpen} 
        activeMenu={activeMenu} 
        setActiveMenu={setActiveMenu} 
        activePath={activePath} 
        setActivePath={setActivePath} 
      />
      <AppContext 
        menuList={menuList} 
        isMobileMenuOpen={isMobileMenuOpen} 
        activeMenu={activeMenu} 
        setActiveMenu={setActiveMenu} 
        activePath={activePath} 
        setActivePath={setActivePath}
      >
        <Outlet />
      </AppContext>
    </>
  );
};

const App = () => {
  return (
    <div className="app-layout">
      <Router>
        <Routes>
          {/* Authentication Routes */}
          <Route path="/authentication/forgotpassword" element={
            <PageLoader>
              <ForgotPassword />
            </PageLoader>
          } />
          <Route path="/authentication/lockscreen" element={
            <PageLoader>
              <LockScreen />
            </PageLoader>
          } />
          <Route path="/" element={
            <PageLoader>
              <Login />
            </PageLoader>
          } />
          <Route path="/authentication/register" element={
            <PageLoader>
              <Register />
            </PageLoader>
          } />
          <Route path="/authentication/otp" element={
            <PageLoader>
              <OTP />
            </PageLoader>
          } />

          {/* Main App Layout Routes */}
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={
              <PageLoader>
                <AdminDashboard />
              </PageLoader>
            } />
            
            {/* Hotel Routes */}
            <Route path="/reservation" element={
              <PageLoader>
                <Reservation />
              </PageLoader>
            } />
            <Route path="/ReservationView" element={<ReservationModelView />} />
            <Route path="/ReservationEdit" element={<ReservationListEdit />} />
            <Route path="/add_new_reservation" element={
              <PageLoader>
                <AddNewReservation />
              </PageLoader>
            } />
            <Route path="/booking" element={
              <PageLoader>
                <Booking />
              </PageLoader>
            } />
            <Route path="/room_view" element={
              <PageLoader>
                <RoomView />
              </PageLoader>
            } />
            <Route path="/reservation_view" element={
              <PageLoader>
                <ReservationView />
              </PageLoader>
            } />
            <Route path="/user_reserved_details" element={
              <PageLoader>
                <UserReserved />
              </PageLoader>
            } />
            <Route path="/room_booked_details" element={
              <PageLoader>
                <RoomBooked />
              </PageLoader>
            } />
            <Route path="/settlement_summary" element={
              <PageLoader>
                <SettlementSummary />
              </PageLoader>
            } />
            <Route path="/guest_enquiry" element={
              <PageLoader>
                <GuestEnquiry />
              </PageLoader>
            } />
            <Route path="/employee" element={
              <PageLoader>
                <Employee />
              </PageLoader>
            } />
            <Route path="/task_assign" element={
              <PageLoader>
                <TaskAssign />
              </PageLoader>
            } />
            <Route path="/room_incident_log" element={
              <PageLoader>
                <RoomIncidentLog />
              </PageLoader>
            } />

            {/* Restaurant Routes */}
            <Route path="/floor_layout" element={
              <PageLoader>
                <FloorLayout />
              </PageLoader>
            } />
            <Route path="/view" element={<ViewFloor />} />
            <Route path="/table_master" element={
              <PageLoader>
                <TableMaster />
              </PageLoader>
            } />
            <Route path="/orders" element={
              <PageLoader>
                <Orders />
              </PageLoader>
            } />
            <Route path="/table_reservation" element={
              <PageLoader>
                <TableReservation />
              </PageLoader>
            } />
            <Route path="/menus" element={
              <PageLoader>
                <MenuManagement />
              </PageLoader>
            } />
            <Route path="/kot/main_kitchen" element={
              <PageLoader>
                <MainKitchen />
              </PageLoader>
            } />
            <Route path="/kot/grill" element={
              <PageLoader>
                <Grill />
              </PageLoader>
            } />
            <Route path="/kot/dessert" element={
              <PageLoader>
                <Dessert />
              </PageLoader>
            } />
            <Route path="/kot/bar" element={
              <PageLoader>
                <Bar />
              </PageLoader>
            } />
            <Route path="/billing_payments" element={
              <PageLoader>
                <BillingPayments />
              </PageLoader>
            } />
            <Route path="/stock" element={
              <PageLoader>
                <Stock />
              </PageLoader>
            } />
            <Route path="/recipe_management" element={
              <PageLoader>
                <ReceipeManagement />
              </PageLoader>
            } />
            <Route path="/staff_master" element={
              <PageLoader>
                <StaffMaster />
              </PageLoader>
            } />
            <Route path="/staff_planning" element={
              <PageLoader>
                <StaffPlanning />
              </PageLoader>
            } />
            <Route path="/guest_management" element={
              <PageLoader>
                <GuestManagement />
              </PageLoader>
            } />
            <Route path="/reports_analytics" element={
              <PageLoader>
                <ReportAnalytics />
              </PageLoader>
            } />

            {/* Master Data Routes */}
            <Route path="/facilities" element={
              <PageLoader>
                <Facilities />
              </PageLoader>
            } />
            <Route path="/room_type" element={
              <PageLoader>
                <RoomType />
              </PageLoader>
            } />
            <Route path="/bed_type" element={
              <PageLoader>
                <BedType />
              </PageLoader>
            } />
            <Route path="/hall_floor" element={
              <PageLoader>
                <HallFloor />
              </PageLoader>
            } />
            <Route path="/rooms" element={
              <PageLoader>
                <Rooms />
              </PageLoader>
            } />
            <Route path="/discount_type" element={
              <PageLoader>
                <DiscountType />
              </PageLoader>
            } />
            <Route path="/tax_types" element={
              <PageLoader>
                <TaxTypes />
              </PageLoader>
            } />
            <Route path="/payment_methods" element={
              <PageLoader>
                <PaymentMethods />
              </PageLoader>
            } />
            <Route path="/identification_proof" element={
              <PageLoader>
                <IdentificationProof />
              </PageLoader>
            } />
            <Route path="/currency_country" element={
              <PageLoader>
                <CurrencyCountry />
              </PageLoader>
            } />
            <Route path="/hsk_task_type" element={
              <PageLoader>
                <HskTaskType />
              </PageLoader>
            } />
            <Route path="/complementary" element={
              <PageLoader>
                <Complementary />
              </PageLoader>
            } />
            <Route path="/reservation_status" element={
              <PageLoader>
                <ReservationStatus />
              </PageLoader>
            } />
            <Route path="/department" element={
              <PageLoader>
                <Department />
              </PageLoader>
            } />
            <Route path="/designation" element={
              <PageLoader>
                <Designation />
              </PageLoader>
            } />

          </Route>

        </Routes>
      </Router>
    </div>
  );
};

export default App;