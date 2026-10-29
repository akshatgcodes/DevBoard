import { useState } from "react";
import { localToday } from "../api";
import type { Alert } from "../types";

const KEY = `devboard:dismissed:${localToday()}`;

function readDismissed(): string[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]");
  } catch {
    return [];
  }
}

const id = (a: Alert) => `${a.source}:${a.kind}`;

const ICON: Record<Alert["level"], string> = { danger: "🔥", warning: "📉", info: "⏳" };

export default function StreakBanner({ alerts }: { alerts: Alert[] }) {
  const [dismissed, setDismissed] = useState(readDismissed);
  const visible = alerts.filter((a) => !dismissed.includes(id(a)));

  if (alerts.length === 0) {
    return (
      <div className="banner banner-ok">
        <span>✅</span> All streaks look healthy. Keep it going.
      </div>
    );
  }
  if (visible.length === 0) return null;

  // Dismissals last for today only, so a risk you ignored comes back tomorrow
  const dismiss = (a: Alert) => {
    const next = [...dismissed, id(a)];
    setDismissed(next);
    try {
      localStorage.setItem(KEY, JSON.stringify(next));
    } catch {
      /* storage unavailable: dismiss for this page view only */
    }
  };

  return (
    <div className="banners" role="status">
      {visible.map((a) => (
        <div key={id(a)} className={`banner banner-${a.level}`}>
          <span aria-hidden>{ICON[a.level]}</span>
          <span className="banner-text">{a.message}</span>
          <button className="icon-btn" onClick={() => dismiss(a)} aria-label="Dismiss for today">
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
