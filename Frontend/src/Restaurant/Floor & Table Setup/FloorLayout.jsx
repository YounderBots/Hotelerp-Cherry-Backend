import React, { useState } from "react";
import TableTemplate from "../../stories/TableTemplate";
import { UserPlus, Eye, Pencil, Trash2, X,ToggleLeft,ToggleRight,User } from "lucide-react";
import "./FloorTable.css";
import {useNavigate} from "react-router-dom";

const FloorTable = () => {
  const Navigate=useNavigate();
  const [data, setData] = useState([
    {
      id: 1,
      floorId: "F01",
      floorName: "Indoor Floor",
      description: "Main dining indoor area",
      totalTables: 24,
      seatingCapacity: 75,
      assignedServers: 10,
      currentOrders: 21,
      status: "Active",
      operatingHours: "10:00 AM - 11:00 PM",
      ActiveTables:17,
      InactiveTables:7,
      TotalOrder:45,
    },
    {
      id: 2,
      floorId: "F02",
      floorName: "Outdoor Floor",
      description: "Open air dining",
      totalTables: 30,
      seatingCapacity: 50,
      assignedServers: 20,
      currentOrders: 20,
      status: "Active",
      operatingHours: "11:09 AM - 11:00 PM",
      ActiveTables:22,
      InactiveTables:10,
      TotalOrder:35,
    },
    {
      id: 3,
      floorId: "F03",
      floorName: "Bar",
      description: "Bar & lounge area",
      totalTables: 15,
      seatingCapacity: 60,
      assignedServers: 0,
      currentOrders: 0,
      status: "Inactive",
      operatingHours: "10:00 AM - 5:00 PM",
      ActiveTables:55,
      InactiveTables:2,
      TotalOrder:78,
    },
  ]);

  const serverList =
    ["John Doe",
    "Jane Smith",
    "Michael Brown",
    "Emily Davis",
    ];

  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [searchServer, setSearchServer] = useState("");
  const [selectedServers, setSelectedServers] = useState([]);
  const [selectedFloorId, setSelectedFloorId] = useState(null);

  const initialForm = {
    floorId: "",
    floorName: "",
    description: "",
    status: "Active",
  };

  const [formData, setFormData] = useState(initialForm);

  /* ================= HANDLERS ================= */

  const openAddModal = () => {
    setEditId(null);
    setFormData(initialForm);
    setShowModal(true);
  };

  const viewPage = (row) => {
    Navigate('/view',{
      state:row,
    });
  };
  const closeModal = () => {
    setEditId(null);
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSave = () => {
    if (!formData.floorId || !formData.floorName) return;

    const payload = {
      ...(editId
        ? data.find((i) => i.id === editId)
        : {
          totalTables: 0,
          seatingCapacity: 0,
          assignedServers: 0,
          currentOrders: 0,
        }),
      ...formData,
      id: editId || Date.now(),
    };

    if (editId) {
      setData((prev) =>
        prev.map((item) => (item.id === editId ? payload : item))
      );
    } else {
      setData((prev) => [...prev, payload]);
    }

    closeModal();
  };

  const handleEdit = (row) => {
    setEditId(row.id);
    setFormData({
      floorId: row.floorId,
      floorName: row.floorName,
      description: row.description || "",
      status: row.status,
    });
    setShowModal(true);
  };

  const StatusForFloor = (id) => {
    setData((prev) =>
      prev.map((item) =>
        item.id === id
          ? { ...item, status: item.status === "Active" ? "Inactive" : "Active" }
          : item
      )
    );
  };

  const filteredServers = serverList.filter((name) =>
    name.toLowerCase().includes(searchServer.toLowerCase())
  );

  const openAssignModal = (row) => {
    setSearchServer("");
    setSelectedFloorId(row.id);
    setSelectedServers([]);
    setShowAssignModal(true);
  };

  const closeAssignModal = () => {
    setShowAssignModal(false);
  };

  const ServerNameSelection = (name) => {
    setSelectedServers((prev) =>
      prev.includes(name)
        ? prev.filter((s) => s !== name)
        : [...prev, name]             
    );
  };

  const saveAssignedServers = () => {
    setData((prev) =>
      prev.map((item) =>
        item.id === selectedFloorId
          ? {
              ...item,
              assignedServers: selectedServers.length,
            }
          : item
      )
    );
    closeAssignModal();
  };


  const handleDelete = (id) => {
    setData((prev) => prev.filter((item) => item.id !== id));
  };

  /* ================= UI ================= */

  return (
    <>
      <TableTemplate
        title="Floor Layout"
        hasActionButton
        searchable
        pagination
        exportable
        actionButton={{
          label: "Add Floor",
          onClick: openAddModal,
          size: "medium",
          variant: "primary",
        }}
        columns={[
          { key: "floorId", title: "Floor ID", align: "center" },
          { key: "floorName", title: "Floor Name", align: "center" },
          { key: "totalTables", title: "Total Tables", align: "center" },
          { key: "seatingCapacity", title: "Seating Capacity", align: "center" },
          { key: "assignedServers", title: "Assigned Servers", align: "center" },
          { key: "currentOrders", title: "Current Orders", align: "center" },
          { key: "status", title: "Status", align: "center", type: "badge" },
          {
            key: "actions",
            title: "Actions",
            align: "center",
            type: "custom",
            render: (row) => (
              <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                <button className="table-action-btn view" onClick={() => viewPage(row)}>
                  <Eye size={16} />
                </button>
                <button className="table-action-btn edit" onClick={() => handleEdit(row)}>
                  <Pencil size={16} />
                </button>
                <button className="table-action-btn delete" onClick={() => handleDelete(row.id)}>
                  <Trash2 size={16} />
                </button>
                <button className="table-action-btn status" 
                onClick={()=>StatusForFloor(row.id)}>
                  {row.status === "Active" ? <ToggleRight size={16} /> : <ToggleLeft size={16} />}
                </button>
                <button className="table-action-btn assign" title="Assign Servers" onClick={()=>openAssignModal(row)}>
                  <User size={16} />
                </button>
              </div>
            ),
          },
        ]}
        data={data}
      />


      {/* ================= ADD / EDIT MODAL ================= */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card modal-sm">
            <div className="modal-header">
              <h3>{editId ? "Edit Floor" : "Add Floor"}</h3>
              <button onClick={closeModal}><X size={18} /></button>
            </div>

            <div className="modal-body single">
              <div className="form-group">
                <label>Floor ID</label>
                <input name="floorId" value={formData.floorId} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Floor Name</label>
                <input name="floorName" value={formData.floorName} onChange={handleChange} />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={4}
                  placeholder="Enter floor description"
                  style={{
                    resize: "vertical",
                    minHeight: "90px",
                  }}
                />
              </div>

              <div className="form-group">
                <label>Status</label>
                <select name="status" value={formData.status} onChange={handleChange}>
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                </select>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn secondary" onClick={closeModal}>Close</button>
              <button className="btn primary" onClick={handleSave}>Submit</button>
            </div>
          </div>
        </div>
      )}

      {showAssignModal && (
      <div className="modal-overlay">
        <div className="modal-card modal-md">
          
          <div className="modal-header">
            <h3>Assign Servers</h3>
            <button onClick={closeAssignModal}>
              <X size={18} />
            </button>
          </div>

          <div className="modal-body md-4">
            <input
              type="text"
              placeholder="Search server..."
              value={searchServer}
              onChange={(e) => setSearchServer(e.target.value)}
              style={{
                width: "60%",
                padding: "8px",
                margin: "10px",
              }}
            />

            <div style={{ maxHeight: "200px", overflowY: "auto" }}>
              {filteredServers.length > 0 ? (
                filteredServers.map((name, index) => (
                  <label
                    key={index}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      padding: "6px",
                      borderBottom: "1px solid #eee",
                      cursor: "pointer",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedServers.includes(name)}
                      onChange={() => ServerNameSelection(name)}
                    />
                    {name}
                  </label>
                ))
              ) : (
                <p style={{ textAlign: "center", color: "#999" }}>
                  No servers found
                </p>
              )}
            </div>
          </div>

          <div className="modal-footer">
            <button className="btn secondary" onClick={closeAssignModal}>
              Cancel
            </button>
            <button
              className="btn primary"
              onClick={saveAssignedServers}
              disabled={selectedServers.length === 0}
            >
              Assign ({selectedServers.length})
            </button>
          </div>

        </div>
      </div>
    )}

    </>
  );
};

export default FloorTable;
