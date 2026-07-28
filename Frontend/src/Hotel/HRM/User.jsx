import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  RefreshCw,
  Save,
  X,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import APICall, { ApiError } from "../../APICalls/APICalls";
import "./HRM.css";
import "../Reservation/Reservation.css";

// -------------------------------------------------------------------------
// Constants
// -------------------------------------------------------------------------
// Permission tuples are ordered [uiLabel, backendFlagName, matrixKey].
// matrixKey uses the same keys the backend returns in `permissions: {view, add, edit, delete}`
// so hydration + save both round-trip cleanly.
const PERMISSIONS = [
  { label: "View", flag: "view_permission", matrix: "view" },
  { label: "Create", flag: "create_permission", matrix: "add" },
  { label: "Edit", flag: "edit_permission", matrix: "edit" },
  { label: "Delete", flag: "delete_permission", matrix: "delete" },
];

// -------------------------------------------------------------------------
// Helpers
// -------------------------------------------------------------------------
const readList = (res) =>
  Array.isArray(res?.data) ? res.data : Array.isArray(res?.data?.data) ? res.data.data : [];

const errMsg = (err, fallback) =>
  err instanceof ApiError && err.message ? err.message : fallback;

// Backend returns { data: { menus: [{ id, permissions: {view, add, edit, delete} }] } }
// for GET /user/role_permissions/{role_id}. Normalise to a flat matrix keyed by menu_id.
const parseRolePermissionsResponse = (res) => {
  const menus = res?.data?.menus || res?.data?.data?.menus || [];
  const matrix = {};
  for (const menu of menus) {
    if (!menu?.id) continue;
    matrix[menu.id] = {
      view: !!menu?.permissions?.view,
      add: !!menu?.permissions?.add,
      edit: !!menu?.permissions?.edit,
      delete: !!menu?.permissions?.delete,
    };
  }
  return matrix;
};

// -------------------------------------------------------------------------
// Toast
// -------------------------------------------------------------------------
const Toast = ({ toast, onClose }) => {
  if (!toast) return null;
  const Icon = toast.kind === "success" ? CheckCircle : AlertCircle;
  return (
    <div
      className={`reservation-toast ${toast.kind}`}
      role={toast.kind === "success" ? "status" : "alert"}
      aria-live={toast.kind === "success" ? "polite" : "assertive"}
    >
      <Icon size={18} aria-hidden="true" />
      <span>{toast.text}</span>
      <button
        type="button"
        className="reservation-toast-close"
        onClick={onClose}
        aria-label="Dismiss notification"
      >
        <X size={14} aria-hidden="true" />
      </button>
    </div>
  );
};

// -------------------------------------------------------------------------
// Page
// -------------------------------------------------------------------------
const User = () => {
  const navigate = useNavigate();
  const mounted = useRef(true);

  const [roles, setRoles] = useState([]);
  const [menus, setMenus] = useState([]);
  const [bootstrapError, setBootstrapError] = useState(null);
  const [bootstrapLoading, setBootstrapLoading] = useState(true);

  const [selectedRoleId, setSelectedRoleId] = useState("");
  const [matrix, setMatrix] = useState({}); // { [menu_id]: {view, add, edit, delete} }
  const [initialMatrix, setInitialMatrix] = useState({}); // for dirty comparison
  const [matrixLoading, setMatrixLoading] = useState(false);
  const [matrixError, setMatrixError] = useState(null);

  const [saving, setSaving] = useState(false);
  const [refreshTick, setRefreshTick] = useState(0);
  const [toast, setToast] = useState(null);

  const showToast = useCallback((kind, text) => setToast({ kind, text, at: Date.now() }), []);
  useEffect(() => {
    if (!toast) return undefined;
    const t = setTimeout(() => setToast(null), 4500);
    return () => clearTimeout(t);
  }, [toast]);

  // --------------------------------------------------------------------
  // Bootstrap roles + menus
  // --------------------------------------------------------------------
  useEffect(() => {
    mounted.current = true;
    setBootstrapLoading(true);
    setBootstrapError(null);
    Promise.allSettled([
      APICall.getT("/user/roles"),
      APICall.getT("/user/menus"),
    ]).then(([rRoles, rMenus]) => {
      if (!mounted.current) return;
      const roleList = rRoles.status === "fulfilled" ? readList(rRoles.value) : [];
      const menuList = rMenus.status === "fulfilled" ? readList(rMenus.value) : [];
      setRoles(roleList);
      setMenus(menuList);

      const errs = [];
      if (rRoles.status === "rejected") errs.push(errMsg(rRoles.reason, "roles"));
      if (rMenus.status === "rejected") errs.push(errMsg(rMenus.reason, "menus"));
      setBootstrapError(errs.length ? `Failed to load: ${errs.join(", ")}` : null);
      setBootstrapLoading(false);
    });
    return () => { mounted.current = false; };
  }, [refreshTick]);

  // --------------------------------------------------------------------
  // Whenever the selected role changes, load its permissions
  // --------------------------------------------------------------------
  useEffect(() => {
    if (!selectedRoleId) {
      setMatrix({});
      setInitialMatrix({});
      setMatrixError(null);
      return undefined;
    }
    let alive = true;
    setMatrixLoading(true);
    setMatrixError(null);
    APICall.getT(`/user/role_permissions/${encodeURIComponent(selectedRoleId)}`)
      .then((res) => {
        if (!alive) return;
        const m = parseRolePermissionsResponse(res);
        // Ensure every menu has a full row (backend omits menus with all-false permissions).
        for (const menu of menus) {
          if (!m[menu.id]) m[menu.id] = { view: false, add: false, edit: false, delete: false };
        }
        setMatrix(m);
        setInitialMatrix(JSON.parse(JSON.stringify(m))); // deep clone for dirty compare
      })
      .catch((err) => {
        if (!alive) return;
        setMatrixError(errMsg(err, "Failed to load role permissions."));
      })
      .finally(() => { if (alive) setMatrixLoading(false); });
    return () => { alive = false; };
  }, [selectedRoleId, menus]);

  const handleTogglePermission = (menuId, matrixKey) => {
    setMatrix((prev) => ({
      ...prev,
      [menuId]: {
        ...(prev[menuId] || { view: false, add: false, edit: false, delete: false }),
        [matrixKey]: !prev?.[menuId]?.[matrixKey],
      },
    }));
  };

  const handleToggleAll = (menuId, on) => {
    setMatrix((prev) => ({
      ...prev,
      [menuId]: { view: on, add: on, edit: on, delete: on },
    }));
  };

  const dirtyMenus = useMemo(() => {
    const dirty = [];
    for (const menu of menus) {
      const before = initialMatrix[menu.id] || { view: false, add: false, edit: false, delete: false };
      const after = matrix[menu.id] || { view: false, add: false, edit: false, delete: false };
      if (
        before.view !== after.view ||
        before.add !== after.add ||
        before.edit !== after.edit ||
        before.delete !== after.delete
      ) {
        dirty.push({ menu, before, after });
      }
    }
    return dirty;
  }, [menus, matrix, initialMatrix]);

  const handleSave = async () => {
    if (!selectedRoleId) {
      showToast("error", "Select a role first.");
      return;
    }
    if (dirtyMenus.length === 0) {
      showToast("error", "No changes to save.");
      return;
    }

    setSaving(true);

    // Batch strategy: for each dirty menu, POST (backend rejects with 409 if it exists — then PUT).
    // A future D58 backend batch endpoint would make this one round-trip.
    const results = await Promise.allSettled(
      dirtyMenus.map(async ({ menu, after }) => {
        const body = {
          role_id: Number(selectedRoleId),
          menu_id: Number(menu.id),
          submenu_id: null,
          view_permission: after.view,
          create_permission: after.add,
          edit_permission: after.edit,
          delete_permission: after.delete,
        };
        try {
          await APICall.postT("/user/role_permissions", body);
        } catch (err) {
          if (err instanceof ApiError && err.status === 409) {
            // Row exists — fall back to PUT.
            await APICall.putT("/user/role_permissions", body);
            return;
          }
          throw err;
        }
      }),
    );

    if (!mounted.current) return;
    const failed = results.filter((r) => r.status === "rejected");
    setSaving(false);

    if (failed.length === 0) {
      showToast("success", `Saved permissions for ${dirtyMenus.length} menu(s).`);
      setInitialMatrix(JSON.parse(JSON.stringify(matrix)));
    } else if (failed.length === dirtyMenus.length) {
      showToast("error", errMsg(failed[0].reason, "Failed to save role permissions."));
    } else {
      showToast("error", `${failed.length} of ${dirtyMenus.length} rows failed. First error: ${errMsg(failed[0].reason, "unknown")}`);
    }
  };

  const handleBack = () => navigate("/dashboard");
  const handleRefresh = () => setRefreshTick((n) => n + 1);

  const canSave = Boolean(selectedRoleId) && dirtyMenus.length > 0 && !saving && !matrixLoading;

  return (
    <div className="usr-page">
      <div className="usr-toolbar">
        <button
          type="button"
          className="rmv-back-btn"
          onClick={handleBack}
          aria-label="Back to dashboard"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Back</span>
        </button>
        <div className="usr-header">
          <span className="rmv-eyebrow">HRM</span>
          <h1 className="rmv-title">Role Permissions</h1>
        </div>
        <div className="rmv-toolbar-actions">
          <button
            type="button"
            className="rmv-toolbar-btn"
            onClick={handleRefresh}
            aria-label="Refresh"
            disabled={bootstrapLoading || saving}
          >
            <RefreshCw size={16} aria-hidden="true" />
            <span>Refresh</span>
          </button>
          <button
            type="button"
            className="rmv-toolbar-btn primary"
            onClick={handleSave}
            disabled={!canSave}
            aria-busy={saving}
            aria-label="Save role permissions"
          >
            <Save size={16} aria-hidden="true" />
            <span>{saving ? "Saving…" : `Save${dirtyMenus.length ? ` (${dirtyMenus.length})` : ""}`}</span>
          </button>
        </div>
      </div>

      {bootstrapError && (
        <div className="reservation-alert" role="alert">
          <span>{bootstrapError}</span>
          <button
            type="button"
            className="reservation-alert-action"
            onClick={handleRefresh}
          >
            Retry
          </button>
        </div>
      )}

      {matrixError && (
        <div className="reservation-alert" role="alert">
          <span>{matrixError}</span>
        </div>
      )}

      {bootstrapLoading && (
        <div className="reservation-loading" role="status" aria-live="polite">
          Loading roles and menus…
        </div>
      )}

      {!bootstrapLoading && (
        <>
          <div className="usr-role-picker">
            <label htmlFor="usr-role-select">User Role</label>
            <select
              id="usr-role-select"
              value={selectedRoleId}
              onChange={(e) => setSelectedRoleId(e.target.value)}
              disabled={saving}
            >
              <option value="">— select a role —</option>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.role_name}
                </option>
              ))}
            </select>
          </div>

          {!selectedRoleId && (
            <div className="reservation-empty">
              Select a role above to view and edit its permissions.
            </div>
          )}

          {selectedRoleId && matrixLoading && (
            <div className="reservation-loading" role="status" aria-live="polite">
              Loading role permissions…
            </div>
          )}

          {selectedRoleId && !matrixLoading && menus.length === 0 && (
            <div className="reservation-empty">
              No menus configured. Add menus under HRM → Menus first.
            </div>
          )}

          {selectedRoleId && !matrixLoading && menus.length > 0 && (
            <div className="usr-table-wrap">
              <table className="permission-table" aria-label="Role permissions matrix">
                <caption className="rmv-sr-only">
                  Permissions for the selected role, one row per menu.
                </caption>
                <thead>
                  <tr>
                    <th scope="col" style={{ width: 60 }}>S.No</th>
                    <th scope="col">Module</th>
                    {PERMISSIONS.map((p) => (
                      <th key={p.matrix} scope="col" align="center">{p.label}</th>
                    ))}
                    <th scope="col" align="center">All</th>
                  </tr>
                </thead>
                <tbody>
                  {menus.map((menu, index) => {
                    const row = matrix[menu.id] || { view: false, add: false, edit: false, delete: false };
                    const allOn = row.view && row.add && row.edit && row.delete;
                    return (
                      <tr key={menu.id}>
                        <td>{index + 1}</td>
                        <td>{menu.menu_name || menu.label || `#${menu.id}`}</td>
                        {PERMISSIONS.map((p) => (
                          <td key={p.matrix} align="center">
                            <input
                              type="checkbox"
                              checked={!!row[p.matrix]}
                              onChange={() => handleTogglePermission(menu.id, p.matrix)}
                              disabled={saving}
                              aria-label={`${p.label} permission for ${menu.menu_name || `menu ${menu.id}`}`}
                            />
                          </td>
                        ))}
                        <td align="center">
                          <input
                            type="checkbox"
                            checked={allOn}
                            onChange={(e) => handleToggleAll(menu.id, e.target.checked)}
                            disabled={saving}
                            aria-label={`Toggle all permissions for ${menu.menu_name || `menu ${menu.id}`}`}
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>

              {dirtyMenus.length > 0 && (
                <div className="usr-dirty-note" role="status" aria-live="polite">
                  {dirtyMenus.length} unsaved change{dirtyMenus.length === 1 ? "" : "s"} — click Save to apply.
                </div>
              )}
            </div>
          )}
        </>
      )}

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
};

export default User;
