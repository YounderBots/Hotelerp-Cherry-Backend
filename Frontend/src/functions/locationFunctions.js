const findInChildren = (children, pathname, path) => {
  for (let i = 0; i < children.length; i += 1) {
    const child = children[i];
    const currentPath = [...path, i];

    // Case-insensitive: the router matches `/Identification_Proof` to the
    // `/identification_proof` route, so the sidebar has to highlight the same
    // row rather than fall back to no highlight at all.
    if (child.path && pathname === child.path.toLowerCase()) {
      return currentPath;
    }

    if (Array.isArray(child.children) && child.children.length > 0) {
      const found = findInChildren(child.children, pathname, currentPath);
      if (found) return found;
    }
  }
  return null;
};

/**
 * Locate the top-level menu that owns `pathname` and the click-path to the
 * matching submenu item.
 *
 * Resolution order:
 *   1) exact submenu match anywhere in the tree (preferred — highlights the
 *      leaf the user actually landed on),
 *   2) top-level item whose `path` equals `pathname`,
 *   3) top-level item whose `path` is a proper prefix of `pathname`
 *      (guards against `/reservation` swallowing `/reservation_view`).
 */
const findMenuByPath = (menu, pathname) => {
  if (!Array.isArray(menu) || menu.length === 0) return null;

  // Callers pass the raw `location.pathname`; every comparison below is against
  // a canonical lower-case menu path, so normalise once here (C-081).
  const target = (pathname || "").toLowerCase();

  // 1) Exact submenu leaf match.
  for (let i = 0; i < menu.length; i += 1) {
    const item = menu[i];
    if (Array.isArray(item.children) && item.children.length > 0) {
      const childPath = findInChildren(item.children, target, []);
      if (childPath) {
        return { activeMenu: item, activePath: childPath };
      }
    }
  }

  // 2) Exact top-level match.
  for (let i = 0; i < menu.length; i += 1) {
    const item = menu[i];
    if (item.path && target === item.path.toLowerCase()) {
      return { activeMenu: item, activePath: [] };
    }
  }

  // 3) Proper-prefix top-level match (`/foo` matches `/foo/bar` but not
  //    `/foobar`).
  for (let i = 0; i < menu.length; i += 1) {
    const item = menu[i];
    const itemPath = item.path ? item.path.toLowerCase() : "";
    if (
      itemPath &&
      target.startsWith(itemPath) &&
      (target.length === itemPath.length || target[itemPath.length] === "/")
    ) {
      return { activeMenu: item, activePath: [] };
    }
  }

  return null;
};

export default findMenuByPath;
