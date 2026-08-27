/**
 * TEMPORARY verification harness for the Night Audit dashboard.
 * See na_preview.html. Delete both once the route exists in App.jsx.
 *
 * Mounts only the dashboard, inside the real AuthProvider (which reads the
 * token Playwright puts in localStorage) and a MemoryRouter, so the component
 * runs against the real API exactly as it will once routed.
 */
import React from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import { AuthProvider } from "./src/Context/AuthContext";
import NightAuditDashboard from "./src/Hotel/Night Audit/NightAuditDashboard";
import "./src/index.css";
import "./src/App.css";

createRoot(document.getElementById("root")).render(
    <React.StrictMode>
        <MemoryRouter>
            <AuthProvider>
                {/* .content-area / .main-content reproduce the padding the real
            layout gives a page, so widths measured here match the app. */}
                <div className="content-area">
                    <main className="main-content" id="main-content">
                        <NightAuditDashboard />
                    </main>
                </div>
            </AuthProvider>
        </MemoryRouter>
    </React.StrictMode>,
);
