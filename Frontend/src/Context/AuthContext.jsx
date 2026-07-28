// src/Context/AuthContext.jsx
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { setUnauthorizedHandler } from "../APICalls/APICalls";

const AuthContext = createContext(null);

const TOKEN_KEY = "AuthToken";
const USER_KEY = "user";
const MENUS_KEY = "menus";

const readJson = (key, fallback) => {
    try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
    } catch {
        return fallback;
    }
};

const readToken = () => {
    try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
};

const clearStoredAuth = () => {
    try {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        localStorage.removeItem(MENUS_KEY);
    } catch { /* ignore */ }
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(() => readJson(USER_KEY, null));
    const [menus, setMenus] = useState(() => readJson(MENUS_KEY, []));
    const [token, setToken] = useState(() => readToken());

    const login = useCallback((data) => {
        try {
            localStorage.setItem(TOKEN_KEY, data.access_token);
            localStorage.setItem(USER_KEY, JSON.stringify(data.user || {}));
            localStorage.setItem(MENUS_KEY, JSON.stringify(data.menus || []));
        } catch { /* ignore quota / privacy errors */ }

        setToken(data.access_token || null);
        setUser(data.user || null);
        setMenus(Array.isArray(data.menus) ? data.menus : []);
    }, []);

    const logout = useCallback(() => {
        clearStoredAuth();
        setToken(null);
        setUser(null);
        setMenus([]);
    }, []);

    const isAuthenticated = useCallback(() => {
        if (token) return true;
        return Boolean(readToken());
    }, [token]);

    // Hook API-layer 401 responses into the context so a stale session is
    // cleared everywhere at once and the user is redirected to sign in.
    useEffect(() => {
        setUnauthorizedHandler(() => {
            clearStoredAuth();
            setToken(null);
            setUser(null);
            setMenus([]);
            if (typeof window !== "undefined" && window.location.pathname !== "/") {
                const here = window.location.pathname + window.location.search;
                const nextParam = here && here !== "/" ? `?next=${encodeURIComponent(here)}` : "";
                window.location.replace(`/${nextParam}`);
            }
        });
        return () => setUnauthorizedHandler(null);
    }, []);

    const value = useMemo(
        () => ({ user, menus, token, login, logout, isAuthenticated }),
        [user, menus, token, login, logout, isAuthenticated],
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if (!ctx) {
        throw new Error("useAuth must be used within an <AuthProvider>. Wrap your app in main.jsx.");
    }
    return ctx;
};
