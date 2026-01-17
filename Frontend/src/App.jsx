import React, { useState, useRef, useEffect, Suspense, lazy } from 'react';
import { Search, Home, Users, CalendarCheck, Moon, MessageCircleQuestion, ClipboardCheck, Utensils, Layers, Bell, User, ChevronRight, Menu, X, ChevronDown, Sun } from 'lucide-react';
import './App.css'
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Outlet } from 'react-router-dom';
import DummyContentPage from './DummyContentPage';
import paLogo from './assets/layout/operesto.png'
import useClickOutside from './hooks/useClickOutside';
import findMenuByPath from './functions/locationFunctions';
import { getMenuList, ICON_MAP, MENU } from './Sidemenu';
import Reservation from './Hotel/Reservation/Reservation';
import NightAudit from './Hotel/Night Audit/NightAudit';

const AdminDashboard = lazy(() => import('./Hotel/Dashboard/AdminDashboard'));
const ForgotPassword = lazy(() => import('./Authentication/Pages/ForgotPassword'));
const LockScreen = lazy(() => import('./Authentication/Pages/LockScreen'));
const Login = lazy(() => import('./Authentication/Pages/Login'));
const OTP = lazy(() => import('./Authentication/Pages/OTP'));
const Register = lazy(() => import('./Authentication/Pages/Register'));





const Navbar = ({ isMobileMenuOpen, setIsMobileMenuOpen }) => {
  return (
    <nav className="navbar">
      {/* LEFT */}
      <div className="navbar-left">
        <div className="logo-container">
          {/* <img src={paLogo} alt="Operesto" /> */}
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
        <div className="profile-box">
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
        console.log(hasChildren);

        const isExpanded = activePath[level] === index;
        return (
          <div key={index}>
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

const AppContext = ({ menuList, activeMenu, setActiveMenu, activePath, setActivePath, children }) => {
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
                // setActivePath([0]);
                if (!item.children) navigate(item.path);
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
    isMobileMenuOpen // only active when menu is open
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




  return (<>
    <Navbar sidebarOutsideRef={sidebarOutsideRef} setIsMobileMenuOpen={setIsMobileMenuOpen} isMobileMenuOpen={isMobileMenuOpen} activeMenu={activeMenu} setActiveMenu={setActiveMenu} activePath={activePath} setActivePath={setActivePath} />
    <AppContext menuList={menuList} isMobileMenuOpen={isMobileMenuOpen} activeMenu={activeMenu} setActiveMenu={setActiveMenu} activePath={activePath} setActivePath={setActivePath}>
      <Outlet />
    </AppContext>
  </>)
}





const App = () => {

  return (
    <div className="app-layout">
      <Router>

        <Suspense fallback={<p>loading</p>}>

          <Routes>

            <Route path='/authentication/forgotpassword' element={<ForgotPassword />} />
            <Route path='/authentication/lockscreen' element={<LockScreen />} />
            <Route path='/' element={<Login />} />
            <Route path='/authentication/register' element={<Register />} />
            <Route path='/authentication/otp' element={<OTP />} />
            <Route element={<AppLayout />}>
              <Route path='/dashboard' element={<AdminDashboard />} />
              <Route path='/*' element={<AdminDashboard />} />
              <Route path='/reservation' element={<Reservation />} />
              <Route path='/night-audit' element={<NightAudit />} />
            </Route>
          </Routes>
        </Suspense>
      </Router>
    </div>
  );
};



export default App;