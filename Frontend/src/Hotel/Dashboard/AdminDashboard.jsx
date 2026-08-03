import React, { useState } from "react";
import { LayoutGrid, Hotel as HotelIcon, Utensils, Wine } from "lucide-react";
import "./AdminDashboard.css";

import Tabs, { Tab } from "../../stories/Tabs";
import OverviewTab from "./OverviewTab";
import HotelDashboardTab from "./HotelDashboardTab";
import RestaurantDashboardTab from "../../Restaurant/Dashboard/RestaurantDashboardTab";
import BarDashboardTab from "../../Bar/Dashboard/BarDashboardTab";

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [visited, setVisited] = useState(() => new Set([0]));

  const handleTabChange = (index) => {
    setActiveTab(index);
    setVisited((prev) => (prev.has(index) ? prev : new Set(prev).add(index)));
  };

  return (
    <div className="admin-dashboard">
      <Tabs value={activeTab} onValueChange={handleTabChange} variant="pills">
        <Tab label="Overview" icon={<LayoutGrid size={16} aria-hidden="true" />}>
          {visited.has(0) && <OverviewTab onNavigate={handleTabChange} />}
        </Tab>
        <Tab label="Hotel" icon={<HotelIcon size={16} aria-hidden="true" />}>
          {visited.has(1) && <HotelDashboardTab />}
        </Tab>
        <Tab label="Restaurant" icon={<Utensils size={16} aria-hidden="true" />}>
          {visited.has(2) && <RestaurantDashboardTab />}
        </Tab>
        <Tab label="Bar" icon={<Wine size={16} aria-hidden="true" />}>
          {visited.has(3) && <BarDashboardTab />}
        </Tab>
      </Tabs>
    </div>
  );
};

export default AdminDashboard;
