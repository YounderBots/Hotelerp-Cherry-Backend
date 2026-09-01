import React, { useMemo, useState } from "react";
import Select from "../../stories/Form/Select";
import Checkbox from "../../stories/Form/Checkbox";
import Button from "../../stories/Button";
import ErrorAlert from "../../stories/ErrorAlert";
import Toast from "../../stories/Toast";
import APICall, { ApiError } from "../../APICalls/APICalls";
import { errMsg, readList } from "../../functions/apiHelpers";
import { useApiResource, useApiResources } from "../../hooks/useApiResource";
import { useToast } from "../../hooks/useToast";
import "./HRM.css";

// Role permissions matrix: one row per menu, four permission flags per row.
// Reached from the sidebar item currently labelled "User" (submenus.id 33);
// the screen has always been about role permissions, not user records —
// employee records live on the Employee screen.
const PERMISSIONS = [
  { matrix: "view", api: "view_permission", label: "View" },
  { matrix: "add", api: "create_permission", label: "Add" },
  { matrix: "edit", api: "edit_permission", label: "Edit" },
  { matrix: "delete", api: "delete_permission", label: "Delete" },
];

const EMPTY_ROW = { view: false, add: false, edit: false, delete: false };

/** The permissions endpoint returns rows keyed by menu; fold them into a map. */
const parsePermissions = (res) => {
  const rows = readList(res);
  const map = {};
  for (const row of rows) {
    map[row.menu_id] = {
      view: Boolean(row.view_permission),
      add: Boolean(row.create_permission),
      edit: Boolean(row.edit_permission),
      delete: Boolean(row.delete_permission),
    };
  }
  return map;
};

const User = () => {
  const {
    data: [roles, menus],
    loading,
    error,
  } = useApiResources([
    { fetch: () => APICall.getT("/user/roles"), select: readList, fallback: "Failed to load roles." },
    { fetch: () => APICall.getT("/user/menus"), select: readList, fallback: "Failed to load menus." },
  ]);

  const { toast, showToast } = useToast();

  const [selectedRoleId, setSelectedRoleId] = useState("");
  // Only the operator's unsaved edits live in state. The saved permissions come
  // from the API and the rendered matrix is the two merged, so there is nothing
  // to keep in sync when the role changes — the old version copied the response
  // into state from inside an effect and had to deep-clone a second baseline
  // to diff against.
  const [overrides, setOverrides] = useState({});
  const [saving, setSaving] = useState(false);

  const {
    data: saved,
    loading: matrixLoading,
    error: matrixError,
    reload: reloadPermissions,
  } = useApiResource(
    () => APICall.getT(`/user/role_permissions/${encodeURIComponent(selectedRoleId)}`),
    {
      select: parsePermissions,
      fallback: "Failed to load role permissions.",
      initial: {},
      deps: [selectedRoleId],
      enabled: Boolean(selectedRoleId),
    },
  );

  // The backend omits menus whose flags are all false, so seed every menu.
  const baseline = useMemo(() => {
    const full = {};
    for (const menu of menus) full[menu.id] = saved[menu.id] || { ...EMPTY_ROW };
    return full;
  }, [menus, saved]);

  const matrix = useMemo(() => ({ ...baseline, ...overrides }), [baseline, overrides]);

  const selectRole = (id) => {
    setSelectedRoleId(id);
    setOverrides({});
  };

  const togglePermission = (menuId, key) => {
    setOverrides((prev) => {
      const current = prev[menuId] || baseline[menuId] || EMPTY_ROW;
      return { ...prev, [menuId]: { ...current, [key]: !current[key] } };
    });
  };

  const toggleAll = (menuId, on) => {
    setOverrides((prev) => ({
      ...prev,
      [menuId]: { view: on, add: on, edit: on, delete: on },
    }));
  };

  const dirty = useMemo(
    () =>
      menus
        .map((menu) => ({
          menu,
          before: baseline[menu.id] || EMPTY_ROW,
          after: matrix[menu.id] || EMPTY_ROW,
        }))
        .filter(({ before, after }) => PERMISSIONS.some((p) => before[p.matrix] !== after[p.matrix])),
    [menus, matrix, baseline],
  );

  const handleSave = async () => {
    if (saving) return;
    if (!selectedRoleId) {
      showToast("Select a role first", "error");
      return;
    }
    if (dirty.length === 0) {
      showToast("No changes to save", "error");
      return;
    }

    setSaving(true);
    // POST creates the row; a 409 means it already exists, so fall back to PUT.
    const results = await Promise.allSettled(
      dirty.map(async ({ menu, after }) => {
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
            await APICall.putT("/user/role_permissions", body);
            return;
          }
          throw err;
        }
      }),
    );
    setSaving(false);

    const failed = results.filter((r) => r.status === "rejected");
    if (failed.length === 0) {
      showToast(`Saved permissions for ${dirty.length} menu${dirty.length === 1 ? "" : "s"}`, "success");
      setOverrides({});
      reloadPermissions();
    } else if (failed.length === dirty.length) {
      showToast(errMsg(failed[0].reason, "Failed to save role permissions"), "error");
    } else {
      showToast(
        `${failed.length} of ${dirty.length} rows failed: ${errMsg(failed[0].reason, "unknown error")}`,
        "error",
      );
    }
  };

  const handleReset = () => setOverrides({});

  const selectedRoleName = roles.find((r) => String(r.id) === String(selectedRoleId))?.role_name;

  return (
    <>
      <ErrorAlert message={error} />

      <div className="perm-panel">
        <div className="perm-panel__header">
          <div>
            <h2 className="perm-panel__title">Role Permissions</h2>
            <p className="perm-panel__subtitle">
              Choose a role, then grant it access to each module.
            </p>
          </div>
          <div className="perm-panel__actions">
            <Button variant="secondary" onClick={handleReset} disabled={saving || dirty.length === 0}>
              Reset
            </Button>
            <Button
              variant="primary"
              onClick={handleSave}
              disabled={saving || !selectedRoleId || dirty.length === 0}
            >
              {saving ? "Saving…" : dirty.length ? `Save (${dirty.length})` : "Save"}
            </Button>
          </div>
        </div>

        <div className="perm-panel__picker">
          <Select
            label="Role"
            value={selectedRoleId}
            onChange={(e) => selectRole(e.target.value)}
            placeholder="Select a role"
            disabled={saving || loading}
            options={roles.map((r) => ({ value: r.id, label: r.role_name }))}
          />
        </div>

        <ErrorAlert message={matrixError} />

        {loading && <div className="perm-panel__state">Loading roles and modules…</div>}

        {!loading && !selectedRoleId && (
          <div className="perm-panel__state">Select a role above to view and edit its permissions.</div>
        )}

        {selectedRoleId && matrixLoading && (
          <div className="perm-panel__state">Loading permissions for {selectedRoleName}…</div>
        )}

        {selectedRoleId && !matrixLoading && menus.length === 0 && (
          <div className="perm-panel__state">No modules are configured yet.</div>
        )}

        {selectedRoleId && !matrixLoading && menus.length > 0 && (
          <div className="perm-panel__table-wrap">
            <table className="permission-table" aria-label="Role permissions matrix">
              <caption className="perm-panel__caption">
                Permissions for {selectedRoleName}, one row per module.
              </caption>
              <thead>
                <tr>
                  <th scope="col" className="permission-table__module">Module</th>
                  {PERMISSIONS.map((p) => (
                    <th key={p.matrix} scope="col">{p.label}</th>
                  ))}
                  <th scope="col">All</th>
                </tr>
              </thead>
              <tbody>
                {menus.map((menu) => {
                  const row = matrix[menu.id] || EMPTY_ROW;
                  const allOn = PERMISSIONS.every((p) => row[p.matrix]);
                  // A module with no name is a data problem; "#12" as its label
                  // just moves the confusion into the permissions matrix.
                  const name = menu.menu_name || "Unnamed module";
                  return (
                    <tr key={menu.id}>
                      <td className="permission-table__module" data-label="Module">{name}</td>
                      {PERMISSIONS.map((p) => (
                        <td key={p.matrix} data-label={p.label}>
                          <Checkbox
                            checked={Boolean(row[p.matrix])}
                            onChange={() => togglePermission(menu.id, p.matrix)}
                            disabled={saving}
                            label={`${p.label} — ${name}`}
                            className="permission-table__box"
                          />
                        </td>
                      ))}
                      <td data-label="All">
                        <Checkbox
                          checked={allOn}
                          onChange={(e) => toggleAll(menu.id, e.target.checked)}
                          disabled={saving}
                          label={`All permissions — ${name}`}
                          className="permission-table__box"
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {dirty.length > 0 && (
              <div className="perm-panel__dirty" role="status" aria-live="polite">
                {dirty.length} unsaved change{dirty.length === 1 ? "" : "s"} — click Save to apply.
              </div>
            )}
          </div>
        )}
      </div>

      <Toast {...toast} />
    </>
  );
};

export default User;
