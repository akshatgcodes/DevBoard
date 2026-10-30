<p align="center">
  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24"
       fill="none" stroke="#3fb950" stroke-width="1.5"
       stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/>
  </svg>
</p>

<h1 align="center">DevBoard</h1>

<p align="center">
  <strong>Your GitHub commits, LeetCode solves and daily goals on one page, with a warning before a streak breaks.</strong>
</p>

<p align="center">
  <a href="https://devboard.akshatgcodes.in">
    <img src="https://img.shields.io/badge/live_demo-3fb950-3fb950?style=flat-square" alt="Live Demo">
  </a>
  <img src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/license-GPL--3.0-3fb950?style=flat-square" alt="License">
</p>

---

## What is DevBoard?

Most developer dashboards are profile cards: they show today's numbers and stop there. DevBoard reads the **trend**. It pulls your GitHub contribution calendar and LeetCode submission history, tracks custom daily goals, and fires a banner when a pattern says you're slipping:

> 🔥 Your 9-day GitHub streak ends at midnight. Go ship something.
> 📉 GitHub contributions down 46% week-over-week (28 → 15).
> ⏳ At this pace your LeetCode activity hits zero in about 2 days. Your streak is at risk.

> **Live demo →** [devboard.akshatgcodes.in](https://devboard.akshatgcodes.in)
> Log in with GitHub (read-only `read:user` scope).

---

## What you get

- **Streak risk banner.** Four rules run over every source: streak ends today, week-over-week decline, flatline after a busy fortnight, and a least-squares trend line projecting when activity hits zero. Danger first, dismissible for the day.
- **GitHub heatmap.** A full year via the GraphQL contribution calendar when you log in with GitHub.
- **LeetCode card.** Solved count by difficulty plus a 6-month submission heatmap, from the public profile. No LeetCode login needed.
- **Daily goals.** Set "Solve 2 problems" with a target per day, log progress with +/−, see a 7-day history and a per-goal streak. Goal streaks feed the same risk banner.
- **One source failing doesn't break the page.** GitHub and LeetCode are fetched in parallel, and each error shows on its own card.

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 19 · TypeScript · Vite · hand-rolled SVG heatmap |
| Backend | FastAPI · SQLAlchemy 2 · httpx (async) |
| Database | PostgreSQL in production, SQLite for local dev (same models) |
| Auth | GitHub OAuth (`read:user`), signed session cookie (itsdangerous) |
| Data | GitHub GraphQL + REST events API · LeetCode public GraphQL |
| Tooling | uv · pytest · Vitest · ruff · GitHub Actions |

---

## Run it

```bash
# API → http://localhost:8000/docs
cd backend && uv sync && cp .env.example .env
uv run uvicorn app.main:app --reload

# App → http://localhost:5173
cd frontend && npm install && npm run dev
```

With `DEV_LOGIN=true` (the default in `.env.example`) you can open the dashboard as any public GitHub username without creating an OAuth app. Full details in [docs/SETUP.md](docs/SETUP.md).

---

## Engineering Decisions

**Why is the risk engine pure functions?**
`risk.py` takes `{date: count}` and returns alerts. It has no I/O, so the same rules work for GitHub, LeetCode and goals, and 13 tests cover the edge cases (midnight grace, quiet weeks, rising trends) without mocking anything.

**Why does the browser send "today"?**
A streak is about the user's day, not the server's. Every API call carries the client's local date, so someone in IST doesn't see their streak "break" at 5:30 am.

**Why a Vite proxy in dev instead of relying on CORS?**
Frontend and API share an origin in dev, so the `HttpOnly` session cookie works with no special setup. CORS with credentials is still configured for production, where they're on different domains (`CROSS_SITE_COOKIES=true`).

**What would you do differently in v2?**
Store a daily snapshot of each source in Postgres. The public events API only covers ~90 days, and LeetCode's calendar is a single opaque blob, so trends currently depend on whatever the upstream APIs still return.

More in [docs/DECISIONS.md](docs/DECISIONS.md).

---

## Docs

| Document | Description |
|---|---|
| [PRD](docs/PRD.md) | Product requirements: goals, user stories, non-goals |
| [Architecture](docs/ARCHITECTURE.md) | System design, data flow, API |
| [Decisions](docs/DECISIONS.md) | Every major technical decision and why |
| [Setup](docs/SETUP.md) | Local dev setup and env vars |
| [Deploy](docs/DEPLOY.md) | Deployment notes |
| [Contributing](CONTRIBUTING.md) | How to propose changes |
| [Changelog](CHANGELOG.md) | What changed in each release |
| [Security](SECURITY.md) | How to report a vulnerability |

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
