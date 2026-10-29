import { useState, type FormEvent } from "react";
import { api } from "../api";
import type { Goal } from "../types";

type Props = { goals: Goal[]; onChange: (goals: Goal[]) => void; onLogged: () => void };

export default function GoalsWidget({ goals, onChange, onLogged }: Props) {
  const [title, setTitle] = useState("");
  const [target, setTarget] = useState(1);
  const [error, setError] = useState<string | null>(null);

  const replace = (g: Goal) => onChange(goals.map((x) => (x.id === g.id ? g : x)));

  const add = async (e: FormEvent) => {
    e.preventDefault();
    try {
      onChange([...goals, await api.createGoal(title.trim(), target)]);
      setTitle("");
      setTarget(1);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add goal");
    }
  };

  const log = async (g: Goal, delta: number) => {
    replace(await api.logGoal(g.id, delta));
    // Goal streaks feed the risk banner, so refresh it
    onLogged();
  };

  const remove = async (g: Goal) => {
    if (!confirm(`Delete "${g.title}" and its history?`)) return;
    await api.deleteGoal(g.id);
    onChange(goals.filter((x) => x.id !== g.id));
    onLogged();
  };

  return (
    <div>
      {goals.length === 0 && <p className="muted">No goals yet. Add one, like "Solve 2 problems".</p>}
      <ul className="goals">
        {goals.map((g) => (
          <li key={g.id} className={`goal ${g.done_today ? "goal-done" : ""}`}>
            <div className="goal-main">
              <div className="goal-title">{g.title}</div>
              <div className="goal-meta">
                <span className="dots" aria-label="Last 7 days">
                  {g.week.map((done, i) => (
                    <span key={i} className={`dot ${done ? "dot-on" : ""}`} />
                  ))}
                </span>
                <span className="muted small">{g.streak > 0 ? `🔥 ${g.streak}` : "no streak"}</span>
              </div>
            </div>
            <div className="goal-controls">
              <button className="icon-btn" onClick={() => log(g, -1)} disabled={g.today_count === 0} aria-label="Undo one">
                −
              </button>
              <span className="mono goal-count">
                {g.today_count}/{g.daily_target}
              </span>
              <button className="icon-btn icon-btn-primary" onClick={() => log(g, 1)} aria-label="Log one">
                +
              </button>
              <button className="icon-btn icon-btn-ghost" onClick={() => remove(g)} aria-label="Delete goal">
                🗑
              </button>
            </div>
          </li>
        ))}
      </ul>
      <form onSubmit={add} className="row goal-form">
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="New daily goal" required maxLength={200} />
        <input
          type="number"
          min={1}
          max={100}
          value={target}
          onChange={(e) => setTarget(Number(e.target.value))}
          className="target-input"
          aria-label="Times per day"
          title="Times per day"
        />
        <button className="btn" type="submit">
          Add
        </button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
