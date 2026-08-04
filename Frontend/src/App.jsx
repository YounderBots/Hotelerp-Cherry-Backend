import React, { useState, useRef, useEffect, useMemo, Suspense, lazy } from 'react';
import { Menu, ChevronDown, ChevronRight } from 'lucide-react';
import './App.css'
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Outlet, Navigate } from 'react-router-dom';
import paLogo from './assets/layout/Cherry.png';
import useClickOutside from './hooks/useClickOutside';
import findMenuByPath from './functions/locationFunctions';
import { ICON_MAP, MENU } from './Sidemenu';
import LogoLoaderComponent from './Authentication/Pages/LogoLoaderComponent';
import { useAuth } from './Context/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import NotFound from './components/NotFound';
import RequirePage from './components/RequirePage';

// These six were static imports, which pulled them into the entry bundle and
// defeated the code splitting every other page gets.
const ReservationModelView = lazy(() => import('./Hotel/Reservation/ReservationModelView'));
const ReservationListEdit = lazy(() => import('./Hotel/Reservation/ReservationListEdit'));
const Roles = lazy(() => import('./Hotel/HRM/Roles'));
const Department = lazy(() => import('./Hotel/HRM/Department'));
const Designation = lazy(() => import('./Hotel/HRM/Designation'));
const Shift = lazy(() => import('./Hotel/HRM/Shift'));

// Lazy load all page components
const ForgotPassword = lazy(() => import('./Authentication/Pages/ForgotPassword'));
const LockScreen = lazy(() => import('./Authentication/Pages/LockScreen'));
const Login = lazy(() => import('./Authentication/Pages/Login'));
// OTP is deliberately not imported — see the note beside the auth routes below.
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
const RestaurantRoster = lazy(() => import('./Hotel/HRM/RestaurantRoster'));
const RestaurantShiftPlanning = lazy(() => import('./Hotel/HRM/RestaurantShiftPlanning'));
const BarRoster = lazy(() => import('./Hotel/HRM/BarRoster'));
const BarShiftPlanning = lazy(() => import('./Hotel/HRM/BarShiftPlanning'));
const TaskAssign = lazy(() => import('./Hotel/House Keeper/TaskAssign'));
const RoomIncidentLog = lazy(() => import('./Hotel/House Keeper/RoomIncidentLog'));

// Restaurant Components - Lazy loaded with grouping
const FloorLayout = lazy(() => import('./Restaurant/Floor & Table Setup/FloorLayout'));
const ViewFloor = lazy(() => import('./Restaurant/Floor & Table Setup/FloorPageView'));
const TableMaster = lazy(() => import('./Restaurant/Floor & Table Setup/TableMaster'));
const Orders = lazy(() => import('./Restaurant/Order Management/Orders'));
const TableReservation = lazy(() => import('./Restaurant/Table Reservation/TableReservation'));
const MenuManagement = lazy(() => import('./Restaurant/Menu Management/MenuManagement'));
const ComboDeals = lazy(() => import('./Restaurant/Menu Management/ComboDeals'));
const MainKitchen = lazy(() => import('./Restaurant/Kitchen Orders/MainKitchen'));
const Grill = lazy(() => import('./Restaurant/Kitchen Orders/Grill'));
const Dessert = lazy(() => import('./Restaurant/Kitchen Orders/Dessert'));
const BillingPayments = lazy(() => import('./Restaurant/Billing & Payments/BillingPayments'));
const Stock = lazy(() => import('./Restaurant/Inventory/Stock'));
const ReceipeManagement = lazy(() => import('./Restaurant/Inventory/ReceipeManagement'));
const GuestManagement = lazy(() => import('./Restaurant/Guest Management/GuestManagement'));
const ReportAnalytics = lazy(() => import('./Restaurant/Report & Analytics/ReportAnalytics'));

// Bar Components - Lazy loaded with grouping
const BarFloorLayout = lazy(() => import('./Bar/Floor & Table Setup/FloorLayout'));
const BarTableMaster = lazy(() => import('./Bar/Floor & Table Setup/TableMaster'));
const BarOrders = lazy(() => import('./Bar/Order Management/Orders'));
const BarMenuManagement = lazy(() => import('./Bar/Menu Management/MenuManagement'));
const BarStationDisplay = lazy(() => import('./Bar/Station Display/BarStationDisplay'));
const BarBillingPayments = lazy(() => import('./Bar/Billing & Payments/BarBillingPayments'));
const BarStock = lazy(() => import('./Bar/Inventory/BarStock'));
const BarReceipeManagement = lazy(() => import('./Bar/Inventory/BarReceipeManagement'));
const BarGuestManagement = lazy(() => import('./Bar/Guest Management/BarGuestManagement'));
const BarReportAnalytics = lazy(() => import('./Bar/Report & Analytics/BarReportAnalytics'));

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

// Wraps every routed page: an ErrorBoundary so one page's throw cannot blank
// the whole app, and Suspense for the lazy chunk. Keyed by pathname so the
// boundary clears itself when the user navigates away from a broken page.
const PageLoader = ({ children }) => {
  const location = useLocation();
  return (
    <ErrorBoundary resetKey={location.pathname}>
      <Suspense fallback={<LogoLoaderComponent />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
};

// Authenticated pages additionally go through the RBAC gate.
const Page = ({ children }) => (
  <PageLoader>
    <RequirePage>{children}</RequirePage>
  </PageLoader>
);

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

  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(" ");
  const displayName =
    fullName || user?.name || user?.username || user?.role_name || "Signed in user";
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
  const [activeMenu, setActiveMenu] = useState(null);
  const [activePath, setActivePath] = useState([0]);
  const location = useLocation();
  const { menus } = useAuth();

  // The sidebar is the RBAC menu payload when there is one, the static MENU
  // otherwise, so the shell always renders something usable. This was state
  // written from an effect, which meant every login rendered the static menu
  // first and then re-rendered with the real one.
  const menuList = useMemo(
    () => (Array.isArray(menus) && menus.length > 0 ? menus : MENU),
    [menus],
  );

  // Highlight the active top-level and submenu path for the current URL.
  // These stay as state rather than being derived: the user can also expand a
  // parent entry that has no route of its own, and that choice has to survive
  // until they navigate.
  useEffect(() => {
    if (!menuList.length) return;
    const result = findMenuByPath(menuList, location.pathname);
    if (result) {
      // Synchronising local state to the router is this effect's purpose.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setActiveMenu(result.activeMenu);
       
      setActivePath(result.activePath);
    }
  }, [location.pathname, menuList]);

  // Close mobile drawer whenever the route changes. Nav clicks close it
  // directly; this covers browser back/forward, which nothing else observes.
  useEffect(() => {
    // Reacting to a navigation event, not mirroring a prop.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  return (
    <>
      {/* Lets keyboard and screen-reader users jump past the module rail and
          submenu, which otherwise sit ahead of the content on every page.
          The #main-content target already existed with nothing pointing at it. */}
      <a className="skip-link" href="#main-content">Skip to main content</a>
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
          {/* /authentication/otp is intentionally not routed. The page calls
              POST /verify_otp and POST /resend_otp, and no backend service
              implements either — there is no OTP concept anywhere in the mesh,
              and no login response ever asks for a second factor. Nothing links
              to it, so the only way to reach it was to type the URL, which
              landed on a screen where every action failed. The component is
              kept in Authentication/Pages/OTP.jsx; restore this route once the
              two endpoints exist. */}

          {/* Main App Layout Routes */}
          <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route path="/dashboard" element={
              <Page>
                <AdminDashboard />
              </Page>
            } />

            {/* Hotel Routes */}
            <Route path="/reservation" element={
              <Page>
                <Reservation />
              </Page>
            } />
            <Route path="/ReservationView" element={
              <Page>
                <ReservationModelView />
              </Page>
            } />
            <Route path="/ReservationEdit" element={
              <Page>
                <ReservationListEdit />
              </Page>
            } />
            <Route path="/add_new_reservation" element={
              <Page>
                <AddNewReservation />
              </Page>
            } />
            <Route path="/booking" element={
              <Page>
                <Booking />
              </Page>
            } />
            <Route path="/room_view" element={
              <Page>
                <RoomView />
              </Page>
            } />
            <Route path="/reservation_view" element={
              <Page>
                <ReservationView />
              </Page>
            } />
            <Route path="/user_reserved_details" element={
              <Page>
                <UserReserved />
              </Page>
            } />
            <Route path="/room_booked_details" element={
              <Page>
                <RoomBooked />
              </Page>
            } />
            <Route path="/settlement_summary" element={
              <Page>
                <SettlementSummary />
              </Page>
            } />
            <Route path="/guest_enquiry" element={
              <Page>
                <GuestEnquiry />
              </Page>
            } />
            <Route path="/employee" element={
              <Page>
                <Employee />
              </Page>
            } />
            <Route path="/user" element={
              <Page>
                <User />
              </Page>
            } />
            <Route path="/department" element={
              <Page>
                <Department />
              </Page>
            } />
            <Route path="/designation" element={
              <Page>
                <Designation />
              </Page>
            } />
            <Route path="/roles" element={
              <Page>
                <Roles />
              </Page>
            } />
            <Route path="/shift" element={
              <Page>
                <Shift />
              </Page>
            } />
            <Route path="/restaurant_roster" element={
              <Page>
                <RestaurantRoster />
              </Page>
            } />
            <Route path="/restaurant_shift_planning" element={
              <Page>
                <RestaurantShiftPlanning />
              </Page>
            } />
            <Route path="/bar_roster" element={
              <Page>
                <BarRoster />
              </Page>
            } />
            <Route path="/bar_shift_planning" element={
              <Page>
                <BarShiftPlanning />
              </Page>
            } />
            <Route path="/task_assign" element={
              <Page>
                <TaskAssign />
              </Page>
            } />
            <Route path="/room_incident_log" element={
              <Page>
                <RoomIncidentLog />
              </Page>
            } />

            {/* Restaurant Routes */}
            <Route path="/floor_layout" element={
              <Page>
                <FloorLayout />
              </Page>
            } />
            <Route path="/view" element={
              <Page>
                <ViewFloor />
              </Page>
            } />
            <Route path="/table_master" element={
              <Page>
                <TableMaster />
              </Page>
            } />
            <Route path="/orders" element={
              <Page>
                <Orders />
              </Page>
            } />
            <Route path="/table_reservation" element={
              <Page>
                <TableReservation />
              </Page>
            } />
            <Route path="/menus" element={
              <Page>
                <MenuManagement />
              </Page>
            } />
            <Route path="/combo_deals" element={
              <Page>
                <ComboDeals />
              </Page>
            } />
            <Route path="/kot/main_kitchen" element={
              <Page>
                <MainKitchen />
              </Page>
            } />
            <Route path="/kot/grill" element={
              <Page>
                <Grill />
              </Page>
            } />
            <Route path="/kot/dessert" element={
              <Page>
                <Dessert />
              </Page>
            } />
            <Route path="/billing_payments" element={
              <Page>
                <BillingPayments />
              </Page>
            } />
            <Route path="/stock" element={
              <Page>
                <Stock />
              </Page>
            } />
            <Route path="/recipe_management" element={
              <Page>
                <ReceipeManagement />
              </Page>
            } />
            <Route path="/guest_management" element={
              <Page>
                <GuestManagement />
              </Page>
            } />
            <Route path="/reports_analytics" element={
              <Page>
                <ReportAnalytics />
              </Page>
            } />

            {/* Bar Routes */}
            <Route path="/bar_floor_layout" element={
              <Page>
                <BarFloorLayout />
              </Page>
            } />
            <Route path="/bar_table_master" element={
              <Page>
                <BarTableMaster />
              </Page>
            } />
            <Route path="/bar_orders" element={
              <Page>
                <BarOrders />
              </Page>
            } />
            <Route path="/bar_menus" element={
              <Page>
                <BarMenuManagement />
              </Page>
            } />
            <Route path="/bar_station" element={
              <Page>
                <BarStationDisplay />
              </Page>
            } />
            <Route path="/bar_billing_payments" element={
              <Page>
                <BarBillingPayments />
              </Page>
            } />
            <Route path="/bar_stock" element={
              <Page>
                <BarStock />
              </Page>
            } />
            <Route path="/bar_recipe_management" element={
              <Page>
                <BarReceipeManagement />
              </Page>
            } />
            <Route path="/bar_guest_management" element={
              <Page>
                <BarGuestManagement />
              </Page>
            } />
            <Route path="/bar_reports_analytics" element={
              <Page>
                <BarReportAnalytics />
              </Page>
            } />

            {/* Master Data Routes */}
            <Route path="/facilities" element={
              <Page>
                <Facilities />
              </Page>
            } />
            <Route path="/room_type" element={
              <Page>
                <RoomType />
              </Page>
            } />
            <Route path="/bed_type" element={
              <Page>
                <BedType />
              </Page>
            } />
            <Route path="/hall_floor" element={
              <Page>
                <HallFloor />
              </Page>
            } />
            <Route path="/rooms" element={
              <Page>
                <Rooms />
              </Page>
            } />
            <Route path="/discount_type" element={
              <Page>
                <DiscountType />
              </Page>
            } />
            <Route path="/tax_types" element={
              <Page>
                <TaxTypes />
              </Page>
            } />
            <Route path="/payment_methods" element={
              <Page>
                <PaymentMethods />
              </Page>
            } />
            <Route path="/identification_proof" element={
              <Page>
                <IdentificationProof />
              </Page>
            } />
            <Route path="/currency_country" element={
              <Page>
                <CurrencyCountry />
              </Page>
            } />
            <Route path="/hsk_task_type" element={
              <Page>
                <HskTaskType />
              </Page>
            } />
            <Route path="/complementary" element={
              <Page>
                <Complementary />
              </Page>
            } />
            <Route path="/reservation_status" element={
              <Page>
                <ReservationStatus />
              </Page>
            } />

          </Route>

          {/* Unmatched URLs previously rendered an empty page. */}
          <Route path="*" element={<NotFound />} />

        </Routes>
      </Router>
    </div>
  );
};

export default App;