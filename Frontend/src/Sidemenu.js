import {
    Home,
    Users,
    CalendarCheck,
    Moon,
    MessageCircleQuestion,
    ClipboardCheck,
    Utensils,
    Layers,
    Wine,
} from 'lucide-react';

// Backend-safe icon lookup by string key. Server-provided menu payloads use
// these keys; the local fallback MENU below also uses them (not raw component
// references) so the sidebar renders icons identically whether the menu came
// from AuthContext or the fallback.
export const ICON_MAP = {
    dashboard: Home,
    reservation: CalendarCheck,
    "night-auditing": Moon,
    "guest-enquiry": MessageCircleQuestion,
    "house-keeper": ClipboardCheck,
    hrm: Users,
    restaurant: Utensils,
    bar: Wine,
    "master-data": Layers,
};

export const MENU = [
    {
        id: "dashboard",
        label: "Dashboard",
        icon: "dashboard",
        path: "/dashboard",
    },
    {
        id: "reservation",
        label: "Reservation",
        icon: "reservation",
        path: "/reservation",
        children: [
            { label: "Add New Reservation", path: "/add_new_reservation" },
            { label: "Booking", path: "/booking" },
            { label: "Room View", path: "/room_view" },
            { label: "Reservation View", path: "/reservation_view" },
        ],
    },
    {
        id: "night-auditing",
        label: "Night Audit",
        icon: "night-auditing",
        children: [
            { label: "Run Night Audit", path: "/night_audit" },
            { label: "User Reserved Details", path: "/user_reserved_details" },
            { label: "Room Booked Details", path: "/room_booked_details" },
            { label: "Settlement Summary", path: "/settlement_summary" },
        ],
    },
    {
        id: "guest-enquiry",
        label: "Guest Enquiry",
        icon: "guest-enquiry",
        path: "/guest_enquiry",
    },
    {
        id: "house-keeper",
        label: "House Keeper",
        icon: "house-keeper",
        children: [
            { label: "Task Assign", path: "/task_assign" },
            { label: "Room Incident Log", path: "/room_incident_log" },
        ],
    },
    {
        id: "hrm",
        label: "HRM",
        icon: "hrm",
        children: [
            { label: "Employee", path: "/employee" },
            { label: "User", path: "/user" },
            { label: "Roles", path: "/roles" },
            { label: "Department", path: "/department" },
            { label: "Designation", path: "/designation" },
            { label: "Shift", path: "/shift" },
            { label: "Restaurant Roster", path: "/restaurant_roster" },
            { label: "Restaurant Shift Planning", path: "/restaurant_shift_planning" },
            { label: "Bar Roster", path: "/bar_roster" },
            { label: "Bar Shift Planning", path: "/bar_shift_planning" },
        ],
    },
    {
        id: "restaurant",
        label: "Restaurant",
        icon: "restaurant",
        children: [
            { label: "Menu Management", path: "/menus" },
            { label: "Combo / Package Deals", path: "/combo_deals" },
            {
                label: "Floor & Table Setup",
                children: [
                    { label: "Floor Layout", path: "/floor_layout" },
                    { label: "Table Master", path: "/table_master" },
                ],
            },
            { label: "Order Management", path: "/orders" },
            { label: "Table Reservation", path: "/table_reservation" },
            {
                label: "Kitchen Orders",
                children: [
                    { label: "Main Kitchen", path: "/kot/main_kitchen" },
                    { label: "Grill", path: "/kot/grill" },
                    { label: "Dessert", path: "/kot/dessert" },
                ],
            },
            { label: "Billing & Payments", path: "/billing_payments" },
            {
                label: "Inventory",
                children: [
                    { label: "Stock", path: "/stock" },
                    { label: "Recipe Management", path: "/recipe_management" },
                ],
            },
            { label: "Guest Management", path: "/guest_management" },
            { label: "Report & Analytics", path: "/reports_analytics" },
        ],
    },
    {
        id: "bar",
        label: "Bar",
        icon: "bar",
        children: [
            { label: "Menu Management", path: "/bar_menus" },
            {
                label: "Floor & Table Setup",
                children: [
                    { label: "Floor Layout", path: "/bar_floor_layout" },
                    { label: "Table Master", path: "/bar_table_master" },
                ],
            },
            { label: "Order Management", path: "/bar_orders" },
            { label: "Station Display", path: "/bar_station" },
            { label: "Billing & Payments", path: "/bar_billing_payments" },
            {
                label: "Inventory",
                children: [
                    { label: "Stock", path: "/bar_stock" },
                    { label: "Recipe Management", path: "/bar_recipe_management" },
                ],
            },
            { label: "Guest Management", path: "/bar_guest_management" },
            { label: "Report & Analytics", path: "/bar_reports_analytics" },
        ],
    },
    {
        id: "master-data",
        label: "Master Data",
        icon: "master-data",
        children: [
            { label: "Facilities", path: "/facilities" },
            { label: "Room Type", path: "/room_type" },
            { label: "Bed Type", path: "/bed_type" },
            { label: "Hall / Floor", path: "/hall_floor" },
            { label: "Rooms", path: "/rooms" },
            { label: "Discount Type", path: "/discount_type" },
            { label: "Tax Types", path: "/tax_types" },
            { label: "Payment Methods", path: "/payment_methods" },
            { label: "Identification Proof", path: "/identification_proof" },
            { label: "Currency & Country", path: "/currency_country" },
            { label: "HSK Task Type", path: "/hsk_task_type" },
            { label: "Complementary", path: "/complementary" },
            { label: "Reservation Status", path: "/reservation_status" },
        ],
    },
];
