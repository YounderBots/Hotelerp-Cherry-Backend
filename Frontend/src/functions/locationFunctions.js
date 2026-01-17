const findInChildren = (children, pathname, path) => {
  for (let i = 0; i < children.length; i++) {
    const child = children[i];
    const currentPath = [...path, i];

    if (child.path && pathname === child.path) {
      return currentPath;
    }

    if (child.children) {
      const found = findInChildren(child.children, pathname, currentPath);
      if (found) return found;
    }
  }
  return null;
};

const findMenuByPath = (menu, pathname) => {
  for (let i = 0; i < menu.length; i++) {
    const item = menu[i];

    // Direct match
    if (item.path && pathname.startsWith(item.path)) {
      return {
        activeMenu: item,
        activePath: []
      };
    }

    // Search children
    if (item.children) {
      const result = findInChildren(item.children, pathname, []);
      if (result) {
        return {
          activeMenu: item,
          activePath: result
        };
      }
    }
  }
  return null;
};




export default findMenuByPath;