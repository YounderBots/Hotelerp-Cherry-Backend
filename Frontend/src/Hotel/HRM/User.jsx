import { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import './HRM.css'



const User = () => {
    const [selectedRole, setSelectedRole] = useState("User");
    const [permissions, setPermissions] = useState({});

    const handlePermissionChange = (module, action) => {
        setPermissions((prev) => ({
            ...prev,
            [module]: {
                ...prev[module],
                [action]: !prev?.[module]?.[action],
            },
        }));
    };

    const modules = [
        "Dashboard",
        "Reservation",
        "Night Audit",
        "Guest Enquiry",
        "House Keeper",
        "HRM",
        "Restaurant",
        "Master Data",
    ];

    const permission = ["View", "Edit", "Delete"];

    return (


        <div className="">
            <div>
                <TableTemplate title="User" />
            </div>
           

            <div className="field">
                <label>User Role</label>
                <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                >
                    <option>Manager</option>
                    <option>Admin</option>
                </select>
            </div>

            <table className="permission-table">
                <thead>
                    <tr>
                        <th>Module</th>
                        {permission.map((e) => (
                            <th key={e}>{e}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>

                    {modules.map((module) => (
                        <tr key={module}>
                            <td>{module}</td>
                            {permission.map((e) => (
                                <td key={e}><input type="checkbox"></input></td>
                            ))
                            }
                        </tr>
                    ))}

                </tbody>
            </table>

            <button
                className="save-btn"
                onClick={() =>
                    console.log({
                        role: selectedRole,
                        permissions,
                    })
                }
            >
                Save User Permissions
            </button>
        </div>
    );
};

export default User;
