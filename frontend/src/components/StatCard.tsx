import type { Summary } from "../types";

export default function StatCard({ label, summary, unit }: { label: string; summary?: Summary; unit: string }) {
  if (!summary) return null;
  const { current_streak, longest_streak, this_week, last_week, change_pct, active_today } = summary;
  const trend = change_pct === null ? "" : change_pct >= 0 ? "up" : "down";

  return (
    <div className="stat">
      <div className="label">{label} streak</div>
      <div className="stat-value">
        {current_streak}
        <span className="stat-unit"> day{current_streak === 1 ? "" : "s"}</span>
        {current_streak > 0 && !active_today && <span className="pill pill-danger">not today yet</span>}
      </div>
      <div className="muted small">best {longest_streak}</div>
      <div className="stat-week">
        <span className="mono">{this_week}</span> {unit} this week
        {change_pct !== null && (
          <span className={`trend trend-${trend}`}>
            {change_pct >= 0 ? "▲" : "▼"} {Math.abs(change_pct)}% vs {last_week}
          </span>
        )}
      </div>
    </div>
  );
}
