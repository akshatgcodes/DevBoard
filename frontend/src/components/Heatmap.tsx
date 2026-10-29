import { useEffect, useRef } from "react";
import { CELL, GAP, layout, levels } from "../lib/heatmap";
import type { Day } from "../types";

export default function Heatmap({ days, accent, unit }: { days: Day[]; accent: string; unit: string }) {
  const scroller = useRef<HTMLDivElement>(null);
  // On narrow screens the grid scrolls; start at the most recent weeks, not a year ago
  useEffect(() => {
    const el = scroller.current;
    if (el) el.scrollLeft = el.scrollWidth;
  }, [days]);

  const level = levels(days);
  const { cells, weeks, monthLabels } = layout(days);

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
