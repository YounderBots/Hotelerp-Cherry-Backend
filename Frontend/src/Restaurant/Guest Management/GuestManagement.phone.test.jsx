// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import GuestManagement from "./GuestManagement";

// The screen's own data plumbing: the list is supplied directly and every
// permission is granted, so the test is about the edit form and nothing else.
const GUEST = {
  id: 7,
  guest_code: "G-7",
  first_name: "Priya",
  last_name: "Sharma",
  // Stored E.164, which is what /restaurant/guest writes.
  mobile: "+919876543210",
  email: "priya@example.com",
  guest_type: "Regular",
  food_preferences: ["Jain"],
  special_notes: "",
  loyalty_points: 3,
};

vi.mock("../../hooks/useApiResource", () => ({
  useApiResource: () => ({ data: [GUEST], loading: false, error: null, reload: vi.fn() }),
}));

vi.mock("../../hooks/usePagePermissions", () => ({
  usePagePermissions: () => ({ view: true, add: true, edit: true, delete: true }),
}));

afterEach(() => cleanup());

describe("GuestManagement edit", () => {
  it("prefills the phone field from the guest record and resets it for Add", () => {
    render(<GuestManagement />);

    fireEvent.click(screen.getByRole("button", { name: "Edit guest" }));

    const input = document.querySelector('input[name="mobile"]');
    expect(input).toBeTruthy();
    // National format of the stored E.164, not an empty box.
    expect(input.value).toBe("9876543210");

    // Closing and reopening as Add must leave the field empty.
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    fireEvent.click(screen.getByRole("button", { name: "Add Guest" }));
    expect(document.querySelector('input[name="mobile"]').value).toBe("");
  });
});
