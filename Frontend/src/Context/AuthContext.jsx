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

    // Sign-out has to reach the other tabs.
    //
    // `logout()` clears localStorage, but each tab keeps its own React copy of
    // the token, so a second tab went on believing it was signed in: its
    // `isAuthenticated()` read the state, not storage, and it kept rendering
    // the app until something happened to trigger a 401. Signing out on a
    // shared front-desk machine therefore did not sign the machine out.
    //
    // The `storage` event only fires in the OTHER documents on the origin,
    // which is exactly the ones that need telling.
    useEffect(() => {
        if (typeof window === "undefined") return undefined;
        const onStorage = (e) => {
            if (e.key !== null && e.key !== TOKEN_KEY) return;
            const stored = readToken();
            if (stored) {
                // Signed in elsewhere (or the value changed): adopt it rather
                // than leaving this tab on a token that is no longer current.
                setToken(stored);
                setUser(readJson(USER_KEY, null));
                setMenus(readJson(MENUS_KEY, []));
            } else {
                setToken(null);
                setUser(null);
                setMenus([]);
            }
        };
        window.addEventListener("storage", onStorage);
        return () => window.removeEventListener("storage", onStorage);
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
