

import { Search, Home, Users, CalendarCheck, Moon, MessageCircleQuestion, ClipboardCheck, Utensils, Layers, Bell, User, ChevronRight, Menu, X, ChevronDown, Sun } from 'lucide-react';

export const ICON_MAP = {
    dashboard: Home,
    reservation: CalendarCheck,
    "night-auditing": Moon,
    "guest-enquiry": MessageCircleQuestion,
    "house-keeper": ClipboardCheck,
    hrm: Users,
    restaurant: Utensils,
    "master-data": Layers
};

export const MENU =
    [
        {
            id: "dashboard",
            label: "Dashboard",
            icon: Home,
            path: "/dashboard",
        },
        {
            id: "reservation",
            label: "Reservation",
            icon: CalendarCheck,
            path: "/reservation",
            children: [
                {
                    label: "Add New Reservation",
                    path: "/add_new_reservation"
                },
                {
                    label: "Booking",
                    path: "/booking"
                },
                {
                    label: "Room View",
                    path: "/room_view"
                },
                {
                    label: "Reservation View",
                    path: "/reservation_view"
                }
            ]
        },
        {
            id: "night-auditing",
            label: "Night Audit",
            icon: Moon,
            children: [

                {
                    label: "User Reserved Details",
                    path: "/user_reserved_details"
                },
                {
                    label: "Room Booked Details",
                    path: "/room_booked_details"
                },
                {
                    label: "Settlement Summary",
                    path: "/settlement_summary"
                }


            ]
        },

        {
            id: "guest-enquiry",
            label: "Guest Enquiry",
            icon: MessageCircleQuestion,
            path: "/guest_enquiry",
        },
        {
            id: "house-keeper",
            label: "House Keeper",
            icon: ClipboardCheck,
            children: [
                {
                    label: "Task Assign",
                    path: "/task_assign"
                },
                {
                    label: "Room Incident Log",
                    path: "/room_incident_log"
                }]
        },
        {
            id: "hrm",
            label: "HRM",
            icon: Users,
            path: "/employee",
        },
        {
            id: "restaurant",
            label: "Restaurant",
            icon: Utensils,
            // path: "/dashboard/admin/restaurant",
            children: [

                {
                    label: "Floor & Table Setup",
                    children: [
                        {
                            label: "Floor Layout",
                            path: "/floor_layout"
                        },
                        {
                            label: "Table Master",
                            path: "/table_master"
                        }
                    ]
                },

                {
                    label: "Order Management",
                    path: "/orders"
                },

                {
                    label: "Table Reservation",
                    path: "/table_reservation"
                },

                {
                    label: "Menu Management",
                    path: "/menus"
                },

                {
                    label: "Kitchen Orders",
                    children: [
                        {
                            label: "Main Kitchen",
                            path: "/kot/main_kitchen"
                        },
                        {
                            label: "Grill",
                            path: "/kot/grill"
                        },
                        {
                            label: "Dessert",
                            path: "/kot/dessert"
                        },
                        {
                            label: "Bar",
                            path: "/kot/bar"
                        }
                    ]
                },

                {
                    label: "Billing & Payments",
                    path: "/billing_payments"
                },

                {
                    label: "Inventory",
                    children: [
                        {
                            label: "Stock",
                            path: "/stock"
                        },
                        {
                            label: "Recipe Management",
                            path: "/recipe_management"
                        }
                    ]
                },

                {
                    label: "Staff Management",
                    children: [
                        {
                            label: "Staff Master",
                            path: "/staff_master"
                        },
                        {
                            label: "Staff Planning",
                            path: "/staff_planning"
                        }
                    ]
                },

                {
                    label: "Guest Management",
                    path: "/guest_management"
                },

                {
                    label: "Report & Analytics",
                    path: "/reports_analytics"
                }

            ]
        },

        {
            id: "master-data",
            label: "Master Data",
            icon: Layers,
            // path: "/master_data",
            children: [

                {
                    label: "Facilities",
                    path: "/facilities"
                },

                {
                    label: "Room Type",
                    path: "/room_type"
                },

                {
                    label: "Bed Type",
                    path: "/bed_type"
                },

                {
                    label: "Hall / Floor",
                    path: "/hall_floor"
                },

                {
                    label: "Rooms",
                    path: "/rooms"
                },

                {
                    label: "Discount Type",
                    path: "/discount_type"
                },

                {
                    label: "Tax Types",
                    path: "/tax_types"
                },

                {
                    label: "Payment Methods",
                    path: "/payment_methods"
                },

                {
                    label: "Identification Proof",
                    path: "/identification_proof"
                },

                {
                    label: "Currency & Country",
                    path: "/currency_country"
                },

                {
                    label: "HSK Task Type",
                    path: "/hsk_task_type"
                },

                {
                    label: "Complementary",
                    path: "/complementary"
                },

                {
                    label: "Reservation Status",
                    path: "/reservation_status"
                }

            ]
        },
    ]

export const getMenuList = async () => {
    try {
        const res = await fetch("http://localhost:5000/");

        if (!res.ok) {
            throw new Error(`API failed: ${res.status}`);
        }

        const data = await res.json();

        // ✅ Ensure the API response is an array
        if (!Array.isArray(data.message)) {
            console.warn("Menu API did not return array. Using fallback MENU.");
            return MENU;
        }

        return data;
    } catch (error) {
        console.error("Menu API error. Using fallback MENU.", error);
        return MENU; // ✅ fallback
    }
};



