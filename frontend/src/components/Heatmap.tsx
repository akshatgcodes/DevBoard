import { useEffect, useRef } from "react";
import type { Day } from "../types";

const CELL = 11;
const GAP = 3;
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** Intensity 0–4 relative to this calendar's own busiest days. */
function levels(days: Day[]): (n: number) => number {
  const active = days.map((d) => d.count).filter((n) => n > 0).sort((a, b) => a - b);
  if (active.length === 0) return () => 0;
  const q = (p: number) => active[Math.min(active.length - 1, Math.floor(p * active.length))];
  const [q1, q2, q3] = [q(0.25), q(0.5), q(0.75)];
  return (n) => (n === 0 ? 0 : n <= q1 ? 1 : n <= q2 ? 2 : n <= q3 ? 3 : 4);
}

export default function Heatmap({ days, accent, unit }: { days: Day[]; accent: string; unit: string }) {
  const scroller = useRef<HTMLDivElement>(null);
  // On narrow screens the grid scrolls; start at the most recent weeks, not a year ago
  useEffect(() => {
    const el = scroller.current;
    if (el) el.scrollLeft = el.scrollWidth;
  }, [days]);

  const level = levels(days);
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

  const width = weeks * (CELL + GAP);
  const height = 7 * (CELL + GAP) + 16;

  return (
    <div className="heatmap-scroll" ref={scroller}>
      <svg width={width} height={height} role="img" aria-label={`Activity heatmap, ${unit}`}>
        {monthLabels.map((m) => (
          <text key={m.x} x={m.x} y={10} className="heatmap-month">
            {m.label}
          </text>
        ))}
        {cells.map((d, i) =>
          d ? (
            <rect
              key={d.date}
              x={Math.floor(i / 7) * (CELL + GAP)}
              y={16 + (i % 7) * (CELL + GAP)}
              width={CELL}
              height={CELL}
              rx={2}
              fill={level(d.count) ? accent : "var(--cell-empty)"}
              fillOpacity={level(d.count) ? 0.25 + level(d.count) * 0.1875 : 1}
            >
              <title>{`${d.count} ${unit} on ${d.date}`}</title>
            </rect>
          ) : null,
        )}
      </svg>
    </div>
  );
}
