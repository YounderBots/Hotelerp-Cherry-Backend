// src/context/AuthContext.jsx
import { createContext, useContext, useState } from "react";
 
const AuthContext = createContext();
 
export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(
        JSON.parse(localStorage.getItem("user"))
    );
    const [menus, setMenus] = useState(
        JSON.parse(localStorage.getItem("menus")) || []
 
    );
 
    const login = (data) => {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));
        localStorage.setItem("menus", JSON.stringify(data.menus));
 
        setUser(data.user);
        setMenus(data.menus);
    };
 
    const logout = () => {
        localStorage.clear();
        setUser(null);
        setMenus([]);
    };
 
    return (
        <AuthContext.Provider value={{ user, menus, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
 
export const useAuth = () => useContext(AuthContext);
 
 