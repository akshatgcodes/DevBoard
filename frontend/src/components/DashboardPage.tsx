import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import type { Dashboard, Goal, Me } from "../types";
import StreakBanner from "./StreakBanner";
import Heatmap from "./Heatmap";
import StatCard from "./StatCard";
import LeetCodeCard from "./LeetCodeCard";
import GoalsWidget from "./GoalsWidget";

type Props = { me: Me; onMeChange: (me: Me) => void; onLogout: () => void };

export default function DashboardPage({ me, onMeChange, onLogout }: Props) {
  const [dash, setDash] = useState<Dashboard | null>(null);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setDash(await api.dashboard());
      setLoadError(null);
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : "Failed to load dashboard");
    }
  }, []);

  useEffect(() => {
    refresh();
    api.goals().then(setGoals);
  }, [refresh, me.leetcode_username]);

  return (
    <div className="page">
      <header className="topbar">
        <span className="logo">
          <span className="logo-mark" aria-hidden /> DevBoard
        </span>
        <div className="user">
          {me.avatar_url && <img src={me.avatar_url} alt="" className="avatar" />}
          <span>{me.login}</span>
          <button className="link-btn" onClick={onLogout}>
            Log out
          </button>
        </div>
      </header>

      {loadError && <p className="error">{loadError}</p>}
      {!dash && !loadError && <p className="muted">Fetching your activity…</p>}

      {dash && (
        <>
          <StreakBanner alerts={dash.alerts} />

          <section className="stats">
            <StatCard label="GitHub" summary={dash.summaries.GitHub} unit="contributions" />
            <StatCard label="LeetCode" summary={dash.summaries.LeetCode} unit="submissions" />
          </section>

          <div className="grid">
            <section className="card span-2">
              <h2>GitHub activity</h2>
              {dash.errors.github && <p className="error">{dash.errors.github}</p>}
              {dash.github && (
                <>
                  <Heatmap days={dash.github.calendar} accent="var(--github)" unit="contributions" />
                  {dash.github.source === "public_events" && (
                    <p className="muted small">
                      Dev login: showing public pushes from the last ~90 days. Log in with GitHub for the full
                      year.
                    </p>
                  )}
                </>
              )}
            </section>

            <section className="card">
              <h2>LeetCode</h2>
              <LeetCodeCard data={dash.leetcode} error={dash.errors.leetcode} me={me} onMeChange={onMeChange} />
              {dash.leetcode && (
                <Heatmap days={dash.leetcode.calendar.slice(-182)} accent="var(--leetcode)" unit="submissions" />
              )}
            </section>

            <section className="card">
              <h2>Daily goals</h2>
              <GoalsWidget goals={goals} onChange={setGoals} onLogged={refresh} />
            </section>
          </div>
        </>
      )}
    </div>
  );
}
