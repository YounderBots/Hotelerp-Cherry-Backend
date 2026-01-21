import { useLocation, useNavigate } from "react-router-dom";
import './FloorTable.css';
import Tabs, { Tab } from "../../stories/Tabs";

const ViewFloor = () => {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state) {
    return <p>No data found</p>;
  }

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
                <p>View Table</p>
            </Tab>
            <Tab label="View Orders">
                <p>View Orders</p>
            </Tab>
            <Tab label="View Staff">
                <p>View Staff</p>
            </Tab>
        </Tabs>
        </div>


      <button onClick={() => navigate(-1)}>Back</button>
    </div>
  );
};

export default ViewFloor;
