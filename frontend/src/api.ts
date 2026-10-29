import type { Dashboard, Goal, Me } from "./types";

// Empty in dev (Vite proxies /api and /auth). Set VITE_API_URL when the API is elsewhere.
const BASE = import.meta.env.VITE_API_URL ?? "";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

/** The user's local date, so "today" on the server matches their timezone. */
export function localToday(): string {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const sep = path.includes("?") ? "&" : "?";
  const res = await fetch(`${BASE}${path}${sep}today=${localToday()}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : res.statusText;
    throw new ApiError(res.status, detail);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

const json = (method: string, body?: unknown): RequestInit => ({
  method,
  body: body === undefined ? undefined : JSON.stringify(body),
});

export const api = {
  authConfig: () => request<{ github: boolean; dev_login: boolean }>("/auth/config"),
  githubLoginUrl: `${BASE}/auth/github/login`,
  devLogin: (username: string) => request("/auth/dev-login", json("POST", { username })),
  logout: () => request("/auth/logout", json("POST")),

  me: () => request<Me>("/api/me"),
  setLeetcode: (leetcode_username: string) =>
    request<Me>("/api/me", json("PATCH", { leetcode_username })),
  dashboard: () => request<Dashboard>("/api/dashboard"),

  goals: () => request<Goal[]>("/api/goals"),
  createGoal: (title: string, daily_target: number) =>
    request<Goal>("/api/goals", json("POST", { title, daily_target })),
  logGoal: (id: number, delta: number) =>
    request<Goal>(`/api/goals/${id}/log`, json("POST", { delta })),
  deleteGoal: (id: number) => request<void>(`/api/goals/${id}`, json("DELETE")),
};
