import { describe, expect, it } from "vitest";
import type { Day } from "../types";
import { CELL, GAP, layout, levels } from "./heatmap";

const days = (start: string, counts: number[]): Day[] =>
  counts.map((count, i) => {
    const d = new Date(`${start}T00:00`);
    d.setDate(d.getDate() + i);
    const pad = (n: number) => String(n).padStart(2, "0");
    return { date: `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`, count };
  });

describe("levels", () => {
  it("splits active days into quartiles of this calendar", () => {
    const level = levels(days("2026-01-01", [0, 1, 2, 3, 4, 5, 6, 7, 8]));
    expect([0, 1, 2, 3, 4, 5, 6, 7, 8].map(level)).toEqual([0, 1, 1, 1, 2, 2, 3, 3, 4]);
  });

  it("is all zero for an empty calendar", () => {
    expect(levels(days("2026-01-01", [0, 0, 0]))(5)).toBe(0);
  });
});

describe("layout", () => {
  it("pads the first week so columns start on Sunday", () => {
    // 2026-01-01 is a Thursday
    const { cells, weeks } = layout(days("2026-01-01", Array(10).fill(1)));
    expect(cells.slice(0, 5).map((c) => c?.date ?? null)).toEqual([null, null, null, null, "2026-01-01"]);
    expect(weeks).toBe(2);
  });

  it("labels months, skipping a partial first column", () => {
    const { monthLabels } = layout(days("2026-01-29", Array(40).fill(0)));
    expect(monthLabels.map((m) => m.label)).toEqual(["Feb", "Mar"]);
    expect(monthLabels[0].x).toBe(CELL + GAP);
  });

  it("labels the first column when it starts on a Sunday", () => {
    // 2026-02-01 is a Sunday
    expect(layout(days("2026-02-01", Array(7).fill(0))).monthLabels).toEqual([{ x: 0, label: "Feb" }]);
  });
});
