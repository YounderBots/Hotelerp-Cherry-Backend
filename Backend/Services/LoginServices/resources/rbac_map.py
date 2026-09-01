"""Route -> page permission map for the gateway (GENERATED -- do not hand-edit).

Every external request reaches the operational services through the gateway
proxy (`/{prefix}/{path}`), so this one table is the whole authorisation
surface for the five operational services.

HOW THIS WAS BUILT
    Derived mechanically from the SPA by Backend/tools/build_rbac_map.py: for
    each route in App.jsx, the endpoints its page -- and every component that
    page imports -- actually calls. The mapping therefore reflects how the app
    really uses the API rather than a guess. Regenerate after adding pages or
    endpoints; the tool also reports what it could not attribute.

SEMANTICS
    A row maps (service prefix, path pattern, HTTP method) to the pages that
    legitimately call it. Access is granted when the role holds the method's
    action on ANY listed page.

    Method -> action:  GET=view  POST=create  PUT=edit  DELETE=delete

    Most rows list exactly one page. Multi-page rows are overwhelmingly shared
    reference-data reads (room types, tax types, payment methods) that many
    screens need; requiring permission on all of them would deny legitimate
    users, so ANY is the correct rule.

    `{id}` matches exactly one path segment.
"""

from __future__ import annotations

# (prefix, path pattern, method) -> pages that may call it
ROUTE_PERMISSIONS: dict[tuple[str, str, str], tuple[str, ...]] = {
    # ---- bar ----
    ("bar", "bill", "GET"): ("/bar_billing_payments",),
    ("bar", "bill/generate/{id}", "POST"): ("/bar_billing_payments",),
    ("bar", "bill/{id}", "GET"): ("/bar_billing_payments",),
    ("bar", "bill/{id}/cancel", "PUT"): ("/bar_billing_payments",),
    ("bar", "bill/{id}/payment", "POST"): ("/bar_billing_payments",),
    ("bar", "bot", "GET"): ("/bar_station",),
    ("bar", "bot/item/{id}/status", "PUT"): ("/bar_station",),
    ("bar", "bot/{id}", "GET"): ("/bar_station",),
    ("bar", "bot/{id}/acknowledge", "PUT"): ("/bar_station",),
    ("bar", "bot/{id}/status", "PUT"): ("/bar_station",),
    ("bar", "floor", "GET"): ("/bar_floor_layout", "/bar_roster", "/bar_shift_planning", "/bar_table_master",),
    ("bar", "floor", "POST"): ("/bar_floor_layout",),
    ("bar", "floor/{id}", "DELETE"): ("/bar_floor_layout",),
    ("bar", "floor/{id}", "PUT"): ("/bar_floor_layout",),
    ("bar", "guest", "GET"): ("/bar_guest_management",),
    ("bar", "guest", "POST"): ("/bar_guest_management",),
    ("bar", "guest/{id}", "DELETE"): ("/bar_guest_management",),
    ("bar", "guest/{id}", "GET"): ("/bar_guest_management",),
    ("bar", "guest/{id}", "PUT"): ("/bar_guest_management",),
    ("bar", "inventory_item", "GET"): ("/bar_recipe_management",),
    ("bar", "inventory_item", "POST"): ("/bar_stock",),
    ("bar", "inventory_item/{id}/transactions", "GET"): ("/bar_stock",),
    ("bar", "inventory_stock", "GET"): ("/bar_stock",),
    ("bar", "inventory_stock/adjust", "POST"): ("/bar_stock",),
    ("bar", "inventory_stock/low_stock", "GET"): ("/bar_reports_analytics",),
    ("bar", "menu", "GET"): ("/bar_billing_payments", "/bar_menus", "/bar_orders", "/bar_recipe_management",),
    ("bar", "menu", "POST"): ("/bar_menus",),
    ("bar", "menu/{id}", "DELETE"): ("/bar_menus",),
    ("bar", "menu/{id}", "GET"): ("/bar_menus",),
    ("bar", "menu/{id}", "PUT"): ("/bar_menus",),
    ("bar", "menu/{id}/modifier", "POST"): ("/bar_menus",),
    ("bar", "menu/{id}/recipe", "GET"): ("/bar_recipe_management",),
    ("bar", "menu/{id}/recipe", "POST"): ("/bar_recipe_management",),
    ("bar", "menu/{id}/variant", "POST"): ("/bar_menus",),
    ("bar", "menu_category", "GET"): ("/bar_menus",),
    ("bar", "menu_recipe_counts", "GET"): ("/bar_recipe_management",),
    ("bar", "menu_sub_category", "GET"): ("/bar_menus",),
    ("bar", "modifier/{id}", "DELETE"): ("/bar_menus",),
    ("bar", "modifier/{id}", "PUT"): ("/bar_menus",),
    ("bar", "order", "GET"): ("/bar_billing_payments", "/bar_orders",),
    ("bar", "order", "POST"): ("/bar_orders",),
    ("bar", "order/item/{id}", "DELETE"): ("/bar_orders",),
    ("bar", "order/{id}", "GET"): ("/bar_billing_payments", "/bar_orders",),
    ("bar", "order/{id}/confirm", "POST"): ("/bar_orders",),
    ("bar", "order/{id}/items", "POST"): ("/bar_orders",),
    ("bar", "order/{id}/status", "PUT"): ("/bar_orders",),
    ("bar", "payment_method", "GET"): ("/bar_billing_payments",),
    ("bar", "reports/cancelled_orders", "GET"): ("/bar_reports_analytics", "/dashboard",),
    ("bar", "reports/daily_sales", "GET"): ("/bar_reports_analytics", "/dashboard",),
    ("bar", "reports/item_sales", "GET"): ("/bar_reports_analytics", "/dashboard",),
    ("bar", "reports/payment_mode", "GET"): ("/bar_reports_analytics", "/dashboard",),
    ("bar", "reports/staff_performance", "GET"): ("/bar_reports_analytics",),
    ("bar", "reports/station_performance", "GET"): ("/bar_reports_analytics", "/dashboard",),
    ("bar", "reports/table_turnover", "GET"): ("/bar_reports_analytics", "/dashboard",),
    ("bar", "staff_assignment", "GET"): ("/bar_roster", "/bar_shift_planning",),
    ("bar", "staff_assignment", "POST"): ("/bar_roster", "/bar_shift_planning",),
    ("bar", "staff_assignment/{id}", "DELETE"): ("/bar_shift_planning",),
    ("bar", "staff_assignment/{id}", "PUT"): ("/bar_shift_planning",),
    ("bar", "staff_assignment/{id}/clock_in", "POST"): ("/bar_shift_planning",),
    ("bar", "staff_assignment/{id}/clock_out", "POST"): ("/bar_shift_planning",),
    ("bar", "station", "GET"): ("/bar_menus", "/bar_recipe_management", "/bar_station",),
    ("bar", "table", "GET"): ("/bar_orders", "/bar_table_master",),
    ("bar", "table", "POST"): ("/bar_table_master",),
    ("bar", "table/{id}", "DELETE"): ("/bar_table_master",),
    ("bar", "table/{id}", "PUT"): ("/bar_table_master",),
    ("bar", "upload_image", "POST"): ("/bar_menus",),
    ("bar", "variant/{id}", "DELETE"): ("/bar_menus",),
    ("bar", "variant/{id}", "PUT"): ("/bar_menus",),
    # ---- hotel ----
    ("hotel", "housekeeper_tasks", "GET"): ("/task_assign", "/user_reserved_details",),
    ("hotel", "housekeeper_tasks", "POST"): ("/task_assign",),
    ("hotel", "housekeeper_tasks", "PUT"): ("/task_assign",),
    ("hotel", "housekeeper_tasks/{id}", "DELETE"): ("/task_assign",),
    ("hotel", "inquiry", "GET"): ("/guest_enquiry",),
    ("hotel", "inquiry", "POST"): ("/guest_enquiry",),
    ("hotel", "inquiry", "PUT"): ("/guest_enquiry",),
    ("hotel", "inquiry/{id}", "DELETE"): ("/guest_enquiry",),
    ("hotel", "inquiry/{id}", "GET"): ("/guest_enquiry",),
    ("hotel", "night_audit/history", "GET"): ("/night_audit",),
    ("hotel", "night_audit/preview", "GET"): ("/night_audit", "/room_booked_details", "/settlement_summary",),
    ("hotel", "night_audit/run", "POST"): ("/night_audit",),
    ("hotel", "reports/daily_sales", "GET"): ("/dashboard",),
    ("hotel", "reports/reservation_summary", "GET"): ("/dashboard",),
    ("hotel", "room_availability", "GET"): ("/add_new_reservation", "/reservation",),
    ("hotel", "room_booking", "GET"): ("/booking",),
    ("hotel", "room_booking", "POST"): ("/booking",),
    ("hotel", "room_booking", "PUT"): ("/booking",),
    ("hotel", "room_booking/{id}", "DELETE"): ("/booking",),
    ("hotel", "room_reservation", "GET"): ("/reservation", "/reservation_view",),
    ("hotel", "room_reservation", "POST"): ("/add_new_reservation",),
    ("hotel", "room_reservation", "PUT"): ("/reservation",),
    ("hotel", "room_reservation/{id}", "DELETE"): ("/reservation",),
    ("hotel", "room_reservation/{id}", "GET"): ("/ReservationView",),
    ("hotel", "room_reservation_cancel/{id}", "POST"): ("/reservation",),
    ("hotel", "room_reservation_checkin/{id}", "POST"): ("/reservation",),
    ("hotel", "room_reservation_checkout/{id}", "POST"): ("/reservation",),
    ("hotel", "room_reservation_checkout_preview/{id}", "GET"): ("/reservation",),
    ("hotel", "room_reservation_no_show/{id}", "POST"): ("/reservation",),
    ("hotel", "room_reservation_pay/{id}", "POST"): ("/reservation",),
    ("hotel", "room_reservation_payments/{id}", "GET"): ("/ReservationView", "/reservation",),
    ("hotel", "room_reservation_quote", "POST"): ("/add_new_reservation", "/reservation",),
    ("hotel", "room_reservation_refund/{id}", "POST"): ("/reservation",),
    ("hotel", "roomincident_log", "GET"): ("/room_incident_log",),
    ("hotel", "roomincident_log", "POST"): ("/room_incident_log",),
    ("hotel", "roomincident_log", "PUT"): ("/room_incident_log",),
    ("hotel", "roomincident_log/{id}", "DELETE"): ("/room_incident_log",),
    ("hotel", "templates/static/identity_proofs/{id}", "GET"): ("/add_new_reservation", "/reservation",),
    ("hotel", "templates/static/room_incidents/{id}", "GET"): ("/room_incident_log",),
    ("hotel", "user_activity_log", "GET"): ("/dashboard", "/user_reserved_details",),
    # ---- masterdata ----
    ("masterdata", "bed_type", "POST"): ("/bed_type",),
    ("masterdata", "bed_type", "PUT"): ("/bed_type",),
    ("masterdata", "bed_type/{id}", "DELETE"): ("/bed_type",),
    ("masterdata", "bed_types", "GET"): ("/bed_type", "/rooms",),
    ("masterdata", "complementry", "GET"): ("/add_new_reservation", "/complementary", "/room_type",),
    ("masterdata", "complementry", "POST"): ("/complementary",),
    ("masterdata", "complementry", "PUT"): ("/complementary",),
    ("masterdata", "complementry/{id}", "DELETE"): ("/complementary",),
    ("masterdata", "complementry/{id}", "GET"): ("/complementary",),
    ("masterdata", "country_currency", "GET"): ("/currency_country", "/discount_type", "/employee", "/tax_types",),
    ("masterdata", "country_currency", "POST"): ("/currency_country",),
    ("masterdata", "country_currency", "PUT"): ("/currency_country",),
    ("masterdata", "country_currency/{id}", "DELETE"): ("/currency_country",),
    ("masterdata", "country_currency/{id}", "GET"): ("/currency_country",),
    ("masterdata", "discount", "GET"): ("/add_new_reservation", "/discount_type", "/reservation",),
    ("masterdata", "discount", "POST"): ("/discount_type",),
    ("masterdata", "discount", "PUT"): ("/discount_type",),
    ("masterdata", "discount/{id}", "DELETE"): ("/discount_type",),
    ("masterdata", "facilities", "GET"): ("/facilities",),
    ("masterdata", "facilities", "POST"): ("/facilities",),
    ("masterdata", "facilities", "PUT"): ("/facilities",),
    ("masterdata", "facilities/{id}", "DELETE"): ("/facilities",),
    ("masterdata", "hall_floor", "GET"): ("/hall_floor",),
    ("masterdata", "hall_floor", "POST"): ("/hall_floor",),
    ("masterdata", "hall_floor", "PUT"): ("/hall_floor",),
    ("masterdata", "hall_floor/{id}", "DELETE"): ("/hall_floor",),
    ("masterdata", "identity_proof", "GET"): ("/add_new_reservation", "/identification_proof",),
    ("masterdata", "identity_proof", "POST"): ("/identification_proof",),
    ("masterdata", "identity_proof", "PUT"): ("/identification_proof",),
    ("masterdata", "identity_proof/{id}", "DELETE"): ("/identification_proof",),
    ("masterdata", "payment_methods", "GET"): ("/add_new_reservation", "/payment_methods", "/reservation",),
    ("masterdata", "payment_methods", "POST"): ("/payment_methods",),
    ("masterdata", "payment_methods", "PUT"): ("/payment_methods",),
    ("masterdata", "payment_methods/{id}", "DELETE"): ("/payment_methods",),
    ("masterdata", "reservation_status", "GET"): ("/add_new_reservation", "/reservation", "/reservation_status",),
    ("masterdata", "reservation_status", "POST"): ("/reservation_status",),
    ("masterdata", "reservation_status", "PUT"): ("/reservation_status",),
    ("masterdata", "reservation_status/{id}", "DELETE"): ("/reservation_status",),
    ("masterdata", "room", "GET"): ("/add_new_reservation", "/dashboard", "/reservation", "/room_incident_log", "/room_view", "/rooms", "/task_assign",),
    ("masterdata", "room", "POST"): ("/rooms",),
    ("masterdata", "room", "PUT"): ("/rooms",),
    ("masterdata", "room/{id}", "DELETE"): ("/rooms",),
    ("masterdata", "room/{id}", "GET"): ("/rooms",),
    ("masterdata", "room_types", "GET"): ("/add_new_reservation", "/booking", "/room_type", "/room_view", "/rooms",),
    ("masterdata", "room_types", "POST"): ("/room_type",),
    ("masterdata", "room_types", "PUT"): ("/room_type",),
    ("masterdata", "room_types/{id}", "DELETE"): ("/room_type",),
    ("masterdata", "room_types/{id}", "GET"): ("/room_type",),
    ("masterdata", "task_type", "GET"): ("/hsk_task_type", "/task_assign",),
    ("masterdata", "task_type", "POST"): ("/hsk_task_type",),
    ("masterdata", "task_type", "PUT"): ("/hsk_task_type",),
    ("masterdata", "task_type/{id}", "DELETE"): ("/hsk_task_type",),
    ("masterdata", "tax", "GET"): ("/add_new_reservation", "/reservation", "/tax_types",),
    ("masterdata", "tax", "POST"): ("/tax_types",),
    ("masterdata", "tax", "PUT"): ("/tax_types",),
    ("masterdata", "tax/{id}", "DELETE"): ("/tax_types",),
    ("masterdata", "templates/static/upload_image/{id}", "GET"): ("/rooms",),
    # ---- restaurant ----
    ("restaurant", "bill", "GET"): ("/billing_payments",),
    ("restaurant", "bill/generate/{id}", "POST"): ("/billing_payments",),
    ("restaurant", "bill/{id}", "GET"): ("/billing_payments",),
    ("restaurant", "bill/{id}/cancel", "PUT"): ("/billing_payments",),
    ("restaurant", "bill/{id}/payment", "POST"): ("/billing_payments",),
    ("restaurant", "combo", "GET"): ("/combo_deals",),
    ("restaurant", "combo", "POST"): ("/combo_deals",),
    ("restaurant", "combo/{id}", "DELETE"): ("/combo_deals",),
    ("restaurant", "combo/{id}", "PUT"): ("/combo_deals",),
    ("restaurant", "floor", "GET"): ("/floor_layout", "/restaurant_roster", "/restaurant_shift_planning", "/table_master",),
    ("restaurant", "floor", "POST"): ("/floor_layout",),
    ("restaurant", "floor/{id}", "DELETE"): ("/floor_layout",),
    ("restaurant", "floor/{id}", "PUT"): ("/floor_layout",),
    ("restaurant", "guest", "GET"): ("/guest_management",),
    ("restaurant", "guest", "POST"): ("/guest_management",),
    ("restaurant", "guest/{id}", "DELETE"): ("/guest_management",),
    ("restaurant", "guest/{id}", "GET"): ("/guest_management",),
    ("restaurant", "guest/{id}", "PUT"): ("/guest_management",),
    ("restaurant", "inventory_item", "GET"): ("/recipe_management",),
    ("restaurant", "inventory_item", "POST"): ("/stock",),
    ("restaurant", "inventory_item/{id}/transactions", "GET"): ("/stock",),
    ("restaurant", "inventory_stock", "GET"): ("/stock",),
    ("restaurant", "inventory_stock/adjust", "POST"): ("/stock",),
    ("restaurant", "inventory_stock/low_stock", "GET"): ("/reports_analytics",),
    ("restaurant", "kitchen", "GET"): ("/kot/dessert", "/kot/grill", "/kot/main_kitchen", "/menus", "/recipe_management",),
    ("restaurant", "kot", "GET"): ("/kot/dessert", "/kot/grill", "/kot/main_kitchen",),
    ("restaurant", "kot/item/{id}/status", "PUT"): ("/kot/dessert", "/kot/grill", "/kot/main_kitchen",),
    ("restaurant", "kot/{id}", "GET"): ("/kot/dessert", "/kot/grill", "/kot/main_kitchen",),
    ("restaurant", "kot/{id}/acknowledge", "PUT"): ("/kot/dessert", "/kot/grill", "/kot/main_kitchen",),
    ("restaurant", "kot/{id}/status", "PUT"): ("/kot/dessert", "/kot/grill", "/kot/main_kitchen",),
    ("restaurant", "menu", "GET"): ("/billing_payments", "/combo_deals", "/menus", "/orders", "/recipe_management",),
    ("restaurant", "menu", "POST"): ("/menus",),
    ("restaurant", "menu/{id}", "DELETE"): ("/menus",),
    ("restaurant", "menu/{id}", "GET"): ("/menus",),
    ("restaurant", "menu/{id}", "PUT"): ("/menus",),
    ("restaurant", "menu/{id}/modifier", "POST"): ("/menus",),
    ("restaurant", "menu/{id}/recipe", "GET"): ("/recipe_management",),
    ("restaurant", "menu/{id}/recipe", "POST"): ("/recipe_management",),
    ("restaurant", "menu/{id}/variant", "POST"): ("/menus",),
    ("restaurant", "menu_category", "GET"): ("/menus",),
    ("restaurant", "menu_recipe_counts", "GET"): ("/recipe_management",),
    ("restaurant", "menu_sub_category", "GET"): ("/menus",),
    ("restaurant", "modifier/{id}", "DELETE"): ("/menus",),
    ("restaurant", "modifier/{id}", "PUT"): ("/menus",),
    ("restaurant", "order", "GET"): ("/billing_payments", "/orders", "/view",),
    ("restaurant", "order", "POST"): ("/orders",),
    ("restaurant", "order/item/{id}", "DELETE"): ("/orders",),
    ("restaurant", "order/{id}", "GET"): ("/billing_payments", "/orders",),
    ("restaurant", "order/{id}/confirm", "POST"): ("/orders",),
    ("restaurant", "order/{id}/items", "POST"): ("/orders",),
    ("restaurant", "order/{id}/status", "PUT"): ("/orders",),
    ("restaurant", "payment_method", "GET"): ("/billing_payments",),
    ("restaurant", "reports/average_check_size", "GET"): ("/dashboard",),
    ("restaurant", "reports/cancelled_orders", "GET"): ("/dashboard", "/reports_analytics",),
    ("restaurant", "reports/category_sales", "GET"): ("/dashboard",),
    ("restaurant", "reports/daily_sales", "GET"): ("/dashboard", "/reports_analytics",),
    ("restaurant", "reports/item_sales", "GET"): ("/dashboard", "/reports_analytics",),
    ("restaurant", "reports/kitchen_performance", "GET"): ("/dashboard", "/reports_analytics",),
    ("restaurant", "reports/payment_mode", "GET"): ("/dashboard", "/reports_analytics",),
    ("restaurant", "reports/staff_performance", "GET"): ("/reports_analytics",),
    ("restaurant", "reports/table_turnover", "GET"): ("/dashboard", "/reports_analytics",),
    ("restaurant", "staff_assignment", "GET"): ("/restaurant_roster", "/restaurant_shift_planning", "/view",),
    ("restaurant", "staff_assignment", "POST"): ("/restaurant_roster", "/restaurant_shift_planning",),
    ("restaurant", "staff_assignment/{id}", "DELETE"): ("/restaurant_shift_planning",),
    ("restaurant", "staff_assignment/{id}", "PUT"): ("/restaurant_shift_planning",),
    ("restaurant", "staff_assignment/{id}/clock_in", "POST"): ("/restaurant_shift_planning",),
    ("restaurant", "staff_assignment/{id}/clock_out", "POST"): ("/restaurant_shift_planning",),
    ("restaurant", "table", "GET"): ("/orders", "/table_master", "/table_reservation", "/view",),
    ("restaurant", "table", "POST"): ("/table_master",),
    ("restaurant", "table/{id}", "DELETE"): ("/table_master",),
    ("restaurant", "table/{id}", "PUT"): ("/table_master",),
    ("restaurant", "table_reservation", "GET"): ("/table_reservation",),
    ("restaurant", "table_reservation", "POST"): ("/table_reservation",),
    ("restaurant", "table_reservation/{id}", "PUT"): ("/table_reservation",),
    ("restaurant", "templates/static/upload_image/{id}", "GET"): ("/menus",),
    ("restaurant", "upload_image", "POST"): ("/menus",),
    ("restaurant", "variant/{id}", "DELETE"): ("/menus",),
    ("restaurant", "variant/{id}", "PUT"): ("/menus",),
    # ---- user ----
    ("user", "departments", "GET"): ("/department", "/employee",),
    ("user", "departments", "POST"): ("/department",),
    ("user", "departments", "PUT"): ("/department",),
    ("user", "departments/{id}", "DELETE"): ("/department",),
    ("user", "designations", "GET"): ("/designation", "/employee",),
    ("user", "designations", "POST"): ("/designation",),
    ("user", "designations", "PUT"): ("/designation",),
    ("user", "designations/{id}", "DELETE"): ("/designation",),
    ("user", "menus", "GET"): ("/user",),
    ("user", "role_permissions", "POST"): ("/user",),
    ("user", "role_permissions", "PUT"): ("/user",),
    ("user", "role_permissions/{id}", "GET"): ("/user",),
    ("user", "roles", "GET"): ("/employee", "/roles", "/user",),
    ("user", "roles", "POST"): ("/roles",),
    ("user", "roles", "PUT"): ("/roles",),
    ("user", "roles/{id}", "DELETE"): ("/roles",),
    ("user", "shifts", "GET"): ("/employee", "/shift",),
    ("user", "shifts", "POST"): ("/shift",),
    ("user", "shifts", "PUT"): ("/shift",),
    ("user", "shifts/{id}", "DELETE"): ("/shift",),
    ("user", "templates/static/users/{id}", "GET"): ("/employee",),
    ("user", "users", "GET"): ("/bar_roster", "/bar_shift_planning", "/employee", "/restaurant_roster", "/restaurant_shift_planning", "/room_incident_log", "/task_assign",),
    ("user", "users", "POST"): ("/employee",),
    ("user", "users", "PUT"): ("/employee",),
    ("user", "users/{id}", "DELETE"): ("/employee",),
}

METHOD_ACTION = {"GET": "view", "POST": "create", "PUT": "edit",
                 "PATCH": "edit", "DELETE": "delete"}

# Routes whose HTTP verb does not describe what they DO.
#
# METHOD_ACTION above is a good default and a poor rule for action endpoints.
# A POST that changes an existing record -- check a guest in, take a payment,
# cancel a booking -- is an EDIT of that record, not the creation of a new
# one. Mapping it to `create` means a role granted view+edit on Reservation is
# refused every one of them.
#
# That is not hypothetical. The Front Office role in this database holds
# exactly view+edit on /reservation, and under `enforce` it was denied
# check-in, check-out, payment, refund, cancel, no-show AND the pricing quote
# -- the entire front-desk job -- while still being able to edit the booking
# through the form. The permission a receptionist is given did not match the
# permission the buttons required.
#
# A POST that only READS is `view` for the same reason: /room_reservation_quote
# prices a stay and stores nothing, and is a POST purely because the request
# carries a room list and dates that will not fit in a query string.
ACTION_OVERRIDES: dict[tuple[str, str, str], str] = {
    # ---- hotel: reservation lifecycle acts on a booking that already exists
    ("hotel", "room_reservation_checkin/{id}", "POST"): "edit",
    ("hotel", "room_reservation_checkout/{id}", "POST"): "edit",
    ("hotel", "room_reservation_cancel/{id}", "POST"): "edit",
    ("hotel", "room_reservation_no_show/{id}", "POST"): "edit",
    ("hotel", "room_reservation_pay/{id}", "POST"): "edit",
    ("hotel", "room_reservation_refund/{id}", "POST"): "edit",
    # ---- reads that happen to be POSTs
    ("hotel", "room_reservation_quote", "POST"): "view",
}

# Endpoints the services expose that no page was shown to call. Under
# RBAC_GATEWAY_MODE=enforce these are denied, which is the intended
# fail-closed behaviour: an endpoint nobody has classified should not be
# reachable by everyone. They are listed rather than silently absent so the
# deny is a reviewed decision, and so that wiring one into the UI shows up as
# a diff here on the next run of the generator.
UNCALLED_ENDPOINTS: tuple[tuple[str, str, str], ...] = (
    # ---- bar ----
    ("bar", "bill/{id}/split", "POST"),
    ("bar", "bot/{id}/print", "POST"),
    ("bar", "guest/{id}/address", "POST"),
    ("bar", "guest/{id}/feedback", "POST"),
    ("bar", "guest/{id}/loyalty", "POST"),
    ("bar", "inventory_item/{id}", "PUT"),
    ("bar", "inventory_purchase", "POST"),
    ("bar", "menu_category", "POST"),
    ("bar", "menu_sub_category", "POST"),
    ("bar", "order/item/{id}", "PUT"),
    ("bar", "payment_method", "POST"),
    ("bar", "settings", "GET"),
    ("bar", "settings", "POST"),
    ("bar", "settings/{id}", "PUT"),
    ("bar", "station", "POST"),
    ("bar", "table/{id}", "GET"),
    # ---- hotel ----
    ("hotel", "export_hsk_details", "GET"),
    ("hotel", "export_room_booked_details", "GET"),
    ("hotel", "export_settlement_summary", "GET"),
    ("hotel", "export_user_activity", "GET"),
    ("hotel", "housekeeper_tasks/{id}", "GET"),
    ("hotel", "keeper_info/{id}", "GET"),
    ("hotel", "night_audit/status", "GET"),
    ("hotel", "night_audit/{id}", "GET"),
    ("hotel", "night_audit_process", "GET"),
    ("hotel", "reservation/{id}", "GET"),
    ("hotel", "room_booking/{id}", "GET"),
    ("hotel", "room_sales", "GET"),
    ("hotel", "roomincident_log/{id}", "GET"),
    # ---- masterdata ----
    ("masterdata", "bed_type/{id}", "GET"),
    ("masterdata", "discount/{id}", "GET"),
    ("masterdata", "facilities/{id}", "GET"),
    ("masterdata", "hall_floor/{id}", "GET"),
    ("masterdata", "identity_proof/{id}", "GET"),
    ("masterdata", "payment_methods/{id}", "GET"),
    ("masterdata", "reservation_status/{id}", "GET"),
    ("masterdata", "task_type/{id}", "GET"),
    ("masterdata", "tax/{id}", "GET"),
    # ---- restaurant ----
    ("restaurant", "bill/{id}/split", "POST"),
    ("restaurant", "guest/{id}/address", "POST"),
    ("restaurant", "guest/{id}/feedback", "POST"),
    ("restaurant", "guest/{id}/loyalty", "POST"),
    ("restaurant", "inventory_item/{id}", "PUT"),
    ("restaurant", "inventory_purchase", "POST"),
    ("restaurant", "kitchen", "POST"),
    ("restaurant", "kot/{id}/print", "POST"),
    ("restaurant", "menu_category", "POST"),
    ("restaurant", "menu_sub_category", "POST"),
    ("restaurant", "order/item/{id}", "PUT"),
    ("restaurant", "payment_method", "POST"),
    ("restaurant", "settings", "GET"),
    ("restaurant", "settings", "POST"),
    ("restaurant", "settings/{id}", "PUT"),
    ("restaurant", "table/merge", "POST"),
    ("restaurant", "table/unmerge/{id}", "POST"),
    ("restaurant", "table/{id}", "GET"),
    ("restaurant", "table_reservation/{id}", "GET"),
    ("restaurant", "waitlist", "GET"),
    ("restaurant", "waitlist", "POST"),
    ("restaurant", "waitlist/{id}", "PUT"),
    # ---- user ----
    ("user", "departments/{id}", "GET"),
    ("user", "designations/{id}", "GET"),
    ("user", "menus", "POST"),
    ("user", "menus", "PUT"),
    ("user", "menus/{id}", "DELETE"),
    ("user", "menus/{id}", "GET"),
    ("user", "role_permissions", "GET"),
    ("user", "role_permissions/{id}", "DELETE"),
    ("user", "roles/{id}", "GET"),
    ("user", "shifts/{id}", "GET"),
    ("user", "submenus", "GET"),
    ("user", "submenus", "POST"),
    ("user", "submenus", "PUT"),
    ("user", "submenus/by-menu/{id}", "GET"),
    ("user", "submenus/{id}", "DELETE"),
    ("user", "submenus/{id}", "GET"),
    ("user", "users/{id}", "GET"),
    ("user", "verify_credentials", "POST"),
)

# Detail routes -> the menu pages you reach them from.
#
# A permission claim is keyed by the user's MENU paths, so a routed screen with
# no menu row -- a detail view opened by clicking a row -- can never appear in
# one. A map row naming only such pages would deny everyone, an owner holding
# every permission included. The gateway therefore also accepts the action on a
# page the app navigates here from, which is the rule the UI already follows:
# you arrived from a page you were allowed to open.
PAGE_PARENTS: dict[str, tuple[str, ...]] = {
    "/": ("/authentication/forgotpassword", "/authentication/lockscreen", "/authentication/register",),
    "/ReservationView": ("/dashboard", "/reservation_view",),
    "/authentication/forgotpassword": ("/", "/authentication/lockscreen",),
    "/authentication/register": ("/",),
    "/view": ("/floor_layout",),
}

# Routed screens with no menu row and nothing navigating to them. Nothing can
# open these, so their rows grant nothing; listed so a dead route stays visible
# rather than being mistaken for a permission bug.
UNREACHABLE_ROUTES: tuple[str, ...] = (
)
