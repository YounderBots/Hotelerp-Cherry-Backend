import React, { useState, useRef, useEffect, Suspense, lazy } from 'react';
import { Menu, ChevronDown, ChevronRight } from 'lucide-react';
import './App.css'
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Outlet, Navigate } from 'react-router-dom';
import paLogo from './assets/layout/Cherry.png';
import useClickOutside from './hooks/useClickOutside';
import findMenuByPath from './functions/locationFunctions';
import { ICON_MAP, MENU } from './Sidemenu';
import LogoLoaderComponent from './Authentication/Pages/LogoLoaderComponent';
import ViewFloor from './Restaurant/Floor & Table Setup/FloorPageView';
import { useAuth } from './Context/AuthContext';
import ReservationModelView from './Hotel/Reservation/ReservationModelView';
import ReservationListEdit from './Hotel/Reservation/ReservationListEdit';
import Roles from './Hotel/HRM/Roles';
import Department from './Hotel/HRM/Department';
import Designation from './Hotel/HRM/Designation';
import Shift from './Hotel/HRM/Shift';

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
const User = lazy(() => import('./Hotel/HRM/User'));
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

// Guards the authenticated app shell. Unauthenticated users are bounced
// to the Login page, preserving the intended destination in `?next=`.
const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated()) {
    const next = `${location.pathname}${location.search}`;
    const nextParam = next && next !== "/" ? `?next=${encodeURIComponent(next)}` : "";
    return <Navigate to={`/${nextParam}`} replace />;
  }
  return children;
};

// Prevents an already-authenticated user from re-visiting the login page.
const RedirectIfAuthed = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  if (isAuthenticated()) {
    const next = new URLSearchParams(location.search).get("next");
    const target = next && next.startsWith("/") && !next.startsWith("//") ? next : "/dashboard";
    return <Navigate to={target} replace />;
  }
  return children;
};

const userInitials = (name) => {
  if (!name) return "?";
  const parts = String(name).trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

const Navbar = ({ isMobileMenuOpen, setIsMobileMenuOpen }) => {
  const [profileOpen, setProfileOpen] = useState(false);
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const profileRef = useRef(null);

  const displayName =
    user?.name || user?.username || user?.email || user?.company_email || "Signed in user";
  const displayRole = user?.role_name || user?.role || "Staff";

  useClickOutside(profileRef, () => setProfileOpen(false), profileOpen);

  useEffect(() => {
    if (!profileOpen) return undefined;
    const onKey = (e) => { if (e.key === "Escape") setProfileOpen(false); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [profileOpen]);

  const handleLogout = () => {
    setProfileOpen(false);
    logout();
    navigate("/", { replace: true });
  };

  return (
    <nav className="navbar" role="navigation" aria-label="Primary">
      {/* LEFT */}
      <div className="navbar-left">
        <div className="logo-container">
          <img src={paLogo} alt="Cherry Hotel ERP" />
        </div>
      </div>

      {/* RIGHT */}
      <div className="navbar-right">
        {/* PROFILE */}
        <div className="profile-container" ref={profileRef}>
          <button
            type="button"
            className="profile-box"
            onClick={() => setProfileOpen((v) => !v)}
            aria-haspopup="menu"
            aria-expanded={profileOpen}
            aria-label={`Account menu for ${displayName}`}
          >
            <span className="profile-avatar profile-avatar-initials" aria-hidden="true">
              {userInitials(displayName)}
            </span>
            <span className="profile-info">
              <span className="profile-name">{displayName}</span>
              <span className="profile-role">{displayRole}</span>
            </span>
            <ChevronDown size={16} aria-hidden="true" />
          </button>

          {profileOpen && (
            <div className="profile-dropdown" role="menu" aria-label="Account menu">
              <button
                type="button"
                className="dropdown-item logout"
                role="menuitem"
                onClick={handleLogout}
              >
                Log out
              </button>
            </div>
          )}
        </div>

        {/* MOBILE MENU */}
        <button
          type="button"
          className="icon-button mobile-only"
          onClick={() => setIsMobileMenuOpen((v) => !v)}
          aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
          aria-expanded={isMobileMenuOpen}
        >
          <Menu size={22} aria-hidden="true" />
        </button>
      </div>
    </nav>
  );
};

const RecursiveMenu = ({ items, activePath, setActivePath, onNavigate, level = 0 }) => {
  const navigate = useNavigate();

  return (
    <>
      {items.map((item, index) => {
        const pathKey = [...activePath.slice(0, level), index];
        const isActive =
          JSON.stringify(activePath.slice(0, level + 1)) ===
          JSON.stringify(pathKey);
        const hasChildren = item.children?.length > 0;
        const isExpanded = activePath[level] === index;

        return (
          <div key={`${item.label}-${level}-${index}`}>
            <button
              type="button"
              className={`sub-item ${isActive ? "active" : ""}`}
              style={{ paddingLeft: `${16 + level * 16}px` }}
              onClick={() => {
                setActivePath(pathKey);
                if (!hasChildren && item.path) {
                  navigate(item.path);
                  if (typeof onNavigate === "function") onNavigate();
                }
              }}
              aria-current={isActive && !hasChildren ? "page" : undefined}
              aria-expanded={hasChildren ? isExpanded : undefined}
            >
              {hasChildren && (
                <span className="submenu-arrow" aria-hidden="true">
                  {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </span>
              )}
              <span>{item.label}</span>
            </button>
            {hasChildren && isExpanded && (
              <RecursiveMenu
                items={item.children}
                activePath={activePath}
                setActivePath={setActivePath}
                onNavigate={onNavigate}
                level={level + 1}
              />
            )}
          </div>
        );
      })}
    </>
  );
};

// Resolve an icon whether the menu item carries a string key (server + new
// fallback MENU) or a raw Lucide component (legacy shape). Never throws.
const resolveIcon = (icon) => {
  if (!icon) return null;
  if (typeof icon === "string") return ICON_MAP[icon] || null;
  return icon;
};

const firstNavigablePath = (item) => {
  if (item?.path) return item.path;
  if (Array.isArray(item?.children)) {
    for (const child of item.children) {
      const found = firstNavigablePath(child);
      if (found) return found;
    }
  }
  return null;
};

const AppContext = ({
  menuList,
  activeMenu,
  setActiveMenu,
  activePath,
  setActivePath,
  isMobileMenuOpen,
  setIsMobileMenuOpen,
  children,
}) => {
  const navigate = useNavigate();
  const mobilePanelRef = useRef(null);

  useClickOutside(
    mobilePanelRef,
    () => setIsMobileMenuOpen(false),
    isMobileMenuOpen,
  );

  useEffect(() => {
    if (!isMobileMenuOpen) return undefined;
    const onKey = (e) => { if (e.key === "Escape") setIsMobileMenuOpen(false); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [isMobileMenuOpen, setIsMobileMenuOpen]);

  const handleTopLevelClick = (item) => {
    setActiveMenu(item);
    const target = firstNavigablePath(item);
    if (target) navigate(target);
  };

  const renderSideNav = (extraClass = "") => (
    <aside className={`side-nav ${extraClass}`} aria-label="Modules">
      {menuList.map((item) => {
        const Icon = resolveIcon(item.icon);
        const isActive = item.id === activeMenu?.id;
        return (
          <button
            type="button"
            key={item.id || item.label}
            className={`nav-item ${isActive ? "active" : ""}`}
            onClick={() => {
              handleTopLevelClick(item);
              setIsMobileMenuOpen(false);
            }}
            aria-current={isActive ? "true" : undefined}
            aria-label={item.label}
          >
            {Icon && <Icon size={22} aria-hidden="true" />}
            <span>{item.label}</span>
          </button>
        );
      })}
    </aside>
  );

  const closeMobile = () => setIsMobileMenuOpen(false);

  const subMenu = Array.isArray(activeMenu?.children) && activeMenu.children.length > 0 && (
    <div className="sub-menu" aria-label={`${activeMenu.label} submenu`}>
      <RecursiveMenu
        items={activeMenu.children}
        activePath={activePath}
        setActivePath={setActivePath}
        onNavigate={closeMobile}
      />
    </div>
  );

  return (
    <div className="app-body">
      {renderSideNav()}
      <div className="content-area">
        {subMenu}
        <main className="main-content" id="main-content">
          {children}
        </main>
      </div>

      {isMobileMenuOpen && (
        <div
          className="mobile-drawer"
          role="dialog"
          aria-modal="true"
          aria-label="Navigation"
        >
          <div className="mobile-panel" ref={mobilePanelRef}>
            {renderSideNav("mobile-side-nav")}
            {subMenu && <div className="mobile-submenu">{subMenu}</div>}
          </div>
        </div>
      )}
    </div>
  );
};

const AppLayout = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [menuList, setMenuList] = useState(MENU);
  const [activeMenu, setActiveMenu] = useState(null);
  const [activePath, setActivePath] = useState([0]);
  const location = useLocation();
  const { menus } = useAuth();

  // Hydrate the sidebar with the RBAC menu payload from AuthContext when it
  // arrives. Falls back to the static MENU when the server returns nothing,
  // so the shell always renders something usable.
  useEffect(() => {
    if (Array.isArray(menus) && menus.length > 0) {
      setMenuList(menus);
    } else {
      setMenuList(MENU);
    }
  }, [menus]);

  // Highlight the active top-level and submenu path for the current URL.
  useEffect(() => {
    if (!menuList.length) return;
    const result = findMenuByPath(menuList, location.pathname);
    if (result) {
      setActiveMenu(result.activeMenu);
      setActivePath(result.activePath);
    }
  }, [location.pathname, menuList]);

  // Close mobile drawer whenever the route changes.
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  return (
    <>
      <Navbar
        setIsMobileMenuOpen={setIsMobileMenuOpen}
        isMobileMenuOpen={isMobileMenuOpen}
      />
      <AppContext
        menuList={menuList}
        isMobileMenuOpen={isMobileMenuOpen}
        setIsMobileMenuOpen={setIsMobileMenuOpen}
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
            <RedirectIfAuthed>
              <PageLoader>
                <Login />
              </PageLoader>
            </RedirectIfAuthed>
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
          <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
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
            <Route path="/user" element={
              <PageLoader>
                <User />
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
            <Route path="/roles" element={
              <PageLoader>
                <Roles />
              </PageLoader>
            } />
            <Route path="/shift" element={
              <PageLoader>
                <Shift />
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

          </Route>

        </Routes>
      </Router>
    </div>
  );
};

export default App;