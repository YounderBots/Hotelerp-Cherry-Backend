import { useLocation, useNavigate } from "react-router";
import './FloorTable.css';
import Tabs, { Tab } from "../../stories/Tabs";
import TableTemplate from "../../stories/TableTemplate";
import { Eye,X } from "lucide-react";
import { useState} from "react";

const ViewFloor = () => {
  const { state } = useLocation();
  const[ViewFlooorTable,setViewFloorTable]=useState(null);
  const [viewOrder,setViewOrder]=useState(null);
  const[viewStaff,setViewStaff]=useState(null);

  if (!state) {
    return <p>No data found</p>;
  }

  const FloorTable=[
    {
      TableID: 'T001',
      TableName: 'Window Side',
      seatingCapacity: 4,
      TableType:'Standard',
      section:'Indoor',
      CurrentStatus:'Active',
      AssignedServer:'John Doe',
    },
    {
      TableID: 'T002',
      TableName: 'Center Hall',
      seatingCapacity: 10,
      TableType:'VIP',
      section:'Outdoor',
      CurrentStatus:'Active',
      AssignedServer:'Jane Smith',
    },
  ];

  const FloorTableColumns = [
    {key:"TableID",title:'Table ID' },
    {key:"TableName",title:'Table Name' },
    {key:"seatingCapacity",title:'Seating Capacity' },
    {key:"TableType",title:'Table Type' },
    {key:"section",title:'Section' },
    {key:"CurrentStatus",title:'Current Status' },
    {key:"AssignedServer",title:'Assigned Server' },
    {
      key: "action",
      title: "Action",
      align: "left",
      type: "custom",
      render: (row) => (
        <button
          className="table-action-btn view"
          onClick={() => setViewFloorTable(row)}
        >
          <Eye size={16} />
        </button>
      ),
    },
  ]

  const orderTable=[
    {
      orderId: 'ORD001',
      tableId: 'T001',
      orderType: 'Dine-In',
      orderTime:'7:00 PM',
      orderStatus:'In Progress',
      AssignedServer:'Alice',
    },
    {
      orderId: 'ORD002',
      tableId: 'T002',
      orderType: 'Takeout',
      orderTime:'8:30 PM',
      orderStatus:'Completed',
      AssignedServer:'Bob',
    }
  ];

  const orderTableColumns=[
    {key:"orderId",title:'Order ID' },
    {key:"tableId",title:'Table ID' },
    {key:"orderType",title:'Order Type' },
    {key:"orderTime",title:'Order Time' },
    {key:"orderStatus",title:'Order Status' },
    {key:"AssignedServer",title:'Assigned Server' },
    {
      key: "action",
      title: "Action",
      align: "left",
      type: "custom",
      render: (row) => (
        <button
          className="table-action-btn view"
          onClick={() => setViewOrder(row)}
        > 
          <Eye size={16} />
        </button>
      ),
    }
  ];

  const StaffTable=[
    {
      StaffId: 'STF001',
      StaffName: 'Emily Johnson',
      Role: 'Server',
      Shift:'Morning',
      ContactNumber:'9888665544',
      AssignedTables:8,
      StaffStatus:'Active',
    },
     {
      StaffId: 'STF002',
      StaffName: 'Ram Kumar',
      Role: 'Waiter',
      Shift:'Night',
      ContactNumber:'9888567891',
      AssignedTables:3,
      StaffStatus:'Active',
    }
  ]

const StaffTableColums = [
  { key: "StaffId", title: "Staff ID" },
  { key: "StaffName", title: "Staff Name" },
  { key: "Role", title: "Role" },
  { key: "Shift", title: "Shift" },
  { key: "ContactNumber", title: "Contact Number" },
  { key: "AssignedTables", title: "Assigned Tables" },
  { key: "StaffStatus", title: "Staff Status" },
  {
    key: "action",
    title: "Action",
    type: "custom",
    render: (row) => (
      <button
        className="table-action-btn view"
        onClick={() => setViewStaff(row)}
        >
        <Eye size={16} />
      </button>
    ),
  },
];




  return (
    <div>
      <h2>Floor Information</h2>
      <div className="form-card">
        <div className="floor-form">
          <div className="form-group">
            <label>Floor ID</label>
            <input type="text" value={state.floorId} readOnly />
          </div>
          <div className="form-group">
            <label>Floor Name</label>
            <input type="text" value={state.floorName} readOnly />
          </div>
          <div className="form-group">
            <label>Floor Status</label>
            <input type="text" value={state.status} readOnly />
         </div>
         <div className="form-group">
            <label>Operational Hours</label>
            <input type="text" value={state.operatingHours} readOnly />
          </div>
          <div className="form-group">
            <label>Total Tables</label>
            <input type="text" value={state.totalTables} readOnly />
          </div>
          <div className="form-group">
            <label>Active Table</label>
            <input type="text" value={state.ActiveTables} readOnly />
          </div>
          <div className="form-group">
            <label>Inactive Tables</label>
            <input type="text" value={state.InactiveTables} readOnly />
          </div>
          <div className="form-group">
            <label>Max Seating Capacity</label>
            <input type="text" value={state.seatingCapacity} readOnly />
          </div>
          <div className="form-group">
            <label>Total Orders</label>
            <input type="text" value={state.TotalOrder} readOnly />
          </div>
          <div className="form-group">
            <label>Current Orders</label>
            <input type="text" value={state.currentOrders} readOnly />
          </div>
          <div className="form-group">
            <label>Total Staff</label>
            <input type="text" value={state.assignedServers} readOnly />
          </div>
        </div>
      </div>

      <div>
         <Tabs varient="default">
            <Tab label="View Tables">
                <TableTemplate 
                  columns={FloorTableColumns} 
                  data={FloorTable} 
                  title="Tables in This Floor"
                />
            </Tab>
            <Tab label="View Orders">
                <TableTemplate 
                  columns={orderTableColumns} 
                  data={orderTable} 
                  title="Orders in This Floor"
                />
            </Tab>
            <Tab label="View Staff">
               <TableTemplate 
               columns={StaffTableColums} 
               data={StaffTable} 
               title="Staff Assigned to the Floor" />
             </Tab>
        </Tabs>
        </div>

        {ViewFlooorTable && (
        <div className="modal-overlay">
          <div className="modal-card large">
            <div className="modal-header">
              <h3>Table Details</h3>
              <button onClick={() => setViewFloorTable(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body grid view">
              {Object.entries(ViewFlooorTable).map(
                ([key, value]) =>
                  key !== "id" && (
                    <div className="form-group" key={key}>
                      <label>{key.replace(/([A-Z])/g, " $1")}</label>
                      <input value={value} disabled />
                    </div>
                  )
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn secondary"
                onClick={() => setViewFloorTable(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {viewOrder && (
        <div className="modal-overlay">
          <div className="modal-card large">
            <div className="modal-header">
              <h3>Order Details</h3>
              <button onClick={() => setViewOrder(null)}>
                <X size={18} />
              </button>
            </div>
            <div className="modal-body grid view">
              {Object.entries(viewOrder).map(
                ([key, value]) =>
                  key !== "id" && (
                    <div className="form-group" key={key}>
                      <label>{key.replace(/([A-Z])/g, " $1")}</label>
                      <input value={value} disabled />
                    </div>
                  )
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn secondary"
                onClick={() => setViewOrder(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

       {viewStaff && (
        <div className="modal-overlay">
          <div className="modal-card large">
            <div className="modal-header">
              <h3>Staff Assigned</h3>
              <button onClick={() => setViewStaff(null)}>
                <X size={18} />
              </button>
            </div>
            <div className="modal-body grid view">
              {Object.entries(viewStaff).map(
                ([key, value]) =>
                  key !== "id" && (
                    <div className="form-group" key={key}>
                      <label>{key.replace(/([A-Z])/g, " $1")}</label>
                      <input value={value} disabled />
                    </div>
                  )
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn secondary"
                onClick={() => setViewStaff(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default ViewFloor;
