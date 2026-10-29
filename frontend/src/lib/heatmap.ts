import type { Day } from "../types";

export const CELL = 11;
export const GAP = 3;
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** Intensity 0–4 relative to this calendar's own busiest days. */
export function levels(days: Day[]): (n: number) => number {
  const active = days.map((d) => d.count).filter((n) => n > 0).sort((a, b) => a - b);
  if (active.length === 0) return () => 0;
  const q = (p: number) => active[Math.min(active.length - 1, Math.floor(p * active.length))];
  const [q1, q2, q3] = [q(0.25), q(0.5), q(0.75)];
  return (n) => (n === 0 ? 0 : n <= q1 ? 1 : n <= q2 ? 2 : n <= q3 ? 3 : 4);
}

/** Week columns and month labels for the grid. */
export function layout(days: Day[]) {
  // Pad the front so the first column starts on a Sunday, like GitHub's grid
  const firstDow = new Date(`${days[0].date}T00:00`).getDay();
  const cells: (Day | null)[] = [...Array(firstDow).fill(null), ...days];
  const weeks = Math.ceil(cells.length / 7);

  const monthLabels: { x: number; label: string }[] = [];
  let lastMonth = -1;
  for (let w = 0; w < weeks; w++) {
    const d = cells[w * 7] ?? cells[w * 7 + 6];
    if (!d) continue;
    const m = new Date(`${d.date}T00:00`).getMonth();
    if (m !== lastMonth) {
      // Skip a label squeezed into the very first partial column
      if (w > 0 || firstDow === 0) monthLabels.push({ x: w * (CELL + GAP), label: MONTHS[m] });
      lastMonth = m;
    }
  }
  return { cells, weeks, monthLabels };
}
