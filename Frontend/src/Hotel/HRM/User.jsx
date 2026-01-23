import { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import './HRM.css'



const User = () => {
    const [selectedRole, setSelectedRole] = useState();
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
    const Roles = ["Admin", "Manager"]

    return (

        <div className="user-container">

            <h2>User</h2>

            <div className="field">
                <label>User Role</label>
                <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                >
                    {Roles.map((e) => (
                        <option>{e}</option>
                    ))}
                </select>
            </div>

            <table className="permission-table">
                <thead>
                    <tr>
                        <th>S.no</th>
                        <th>Module</th>
                        {permission.map((e) => (
                            <th key={e}>{e}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>

                    {modules.map((module, index) => (
                        <tr key={index}>
                            <td>{index + 1}</td>
                            <td>{module}</td>
                            {permission.map((e) => (
                                <td key={e}>
                                    <input type="checkbox" checked={permissions?.[module]?.[e] || false}
                                        onChange={() => handlePermissionChange(module, e)}></input></td>
                            ))
                            }
                        </tr>
                    ))}

                </tbody>
            </table>

            <div className="save-btn">
                <button
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
        </div>


    );
};

export default User;
