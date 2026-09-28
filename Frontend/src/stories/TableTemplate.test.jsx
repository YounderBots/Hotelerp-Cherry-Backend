// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import TableTemplate from "./TableTemplate";

afterEach(() => cleanup());

describe("TableTemplate sorting", () => {
  it("exposes each sortable header as a labelled button and changes row order", () => {
    render(
      <TableTemplate
        title="Facilities"
        columns={[{ key: "name", title: "Facility name" }]}
        data={[
          { id: 1, name: "Zulu" },
          { id: 2, name: "Alpha" },
          { id: 3, name: "Mike" },
        ]}
        pagination={false}
        exportable={false}
      />,
    );

    const sortButton = screen.getByRole("button", { name: "Sort by Facility name" });
    expect(sortButton).toBeTruthy();

    const names = () =>
      [...document.querySelectorAll("table.table tbody tr:not(.table-message-row) td:nth-child(2)")].map(
        (cell) => cell.textContent,
      );

    expect(names()).toEqual(["Zulu", "Alpha", "Mike"]);
    fireEvent.click(sortButton);
    expect(names()).toEqual(["Alpha", "Mike", "Zulu"]);
    expect(sortButton.closest("th")?.getAttribute("aria-sort")).toBe("ascending");

    fireEvent.click(sortButton);
    expect(names()).toEqual(["Zulu", "Mike", "Alpha"]);
    expect(sortButton.closest("th")?.getAttribute("aria-sort")).toBe("descending");
  });

  it("exposes the column filter as a named dialog and closes it with Escape", () => {
    render(
      <TableTemplate
        columns={[{ key: "name", title: "Name" }]}
        data={[{ id: 1, name: "Alpha" }]}
        pagination={false}
        exportable={false}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Choose which columns are visible" }));
    expect(screen.getByRole("dialog", { name: "Column Visibility" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Close column visibility" })).toBeTruthy();

    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog", { name: "Column Visibility" })).toBeNull();
  });
});
