import { useState, type FormEvent } from "react";
import { api } from "../api";
import type { Dashboard, Me } from "../types";

type Props = {
  data: Dashboard["leetcode"];
  error?: string;
  me: Me;
  onMeChange: (me: Me) => void;
};

const DIFFS = ["easy", "medium", "hard"] as const;

export default function LeetCodeCard({ data, error, me, onMeChange }: Props) {
  const [editing, setEditing] = useState(!me.leetcode_username);
  const [value, setValue] = useState(me.leetcode_username ?? "");

  const save = async (e: FormEvent) => {
    e.preventDefault();
    onMeChange(await api.setLeetcode(value.trim()));
    setEditing(false);
  };

  if (editing) {
    return (
      <form onSubmit={save} className="lc-form">
        <label htmlFor="lc-user" className="label">
          LeetCode username
        </label>
        <div className="row">
          <input id="lc-user" value={value} onChange={(e) => setValue(e.target.value)} placeholder="your_handle" />
          <button className="btn" type="submit">
            Save
          </button>
        </div>
        <p className="muted small">Only public profile stats are read. No login needed.</p>
      </form>
    );
  }

  const total = data?.solved.all ?? 0;
  return (
    <div>
      <div className="card-head">
        <div>
          <div className="label">Solved</div>
          <div className="stat-value">{total}</div>
        </div>
        <button className="link-btn" onClick={() => setEditing(true)}>
          @{me.leetcode_username} · change
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      {data &&
        DIFFS.map((d) => (
          <div key={d} className="diff-row">
            <span className={`diff diff-${d}`}>{d}</span>
            <div className="bar">
              <div className={`bar-fill diff-bg-${d}`} style={{ width: `${total ? (data.solved[d] / total) * 100 : 0}%` }} />
            </div>
            <span className="mono">{data.solved[d]}</span>
          </div>
        ))}
    </div>
  );
}
