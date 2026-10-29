# Architecture

## Overview

```
┌──────────────────────┐   /api, /auth    ┌──────────────────────────┐
│  React + Vite (5173) │ ───────────────▶ │  FastAPI (8000)          │
│  Login · Dashboard   │   (Vite proxy)   │                          │
│  Heatmap · Goals     │ ◀─────────────── │  auth.py   OAuth+session │
└──────────────────────┘    JSON          │  routers/  me·dashboard  │
                                          │            goals         │
                                          │  risk.py   pure rules    │
                                          │  sources/  github·leetcode│
                                          └──────┬──────────┬────────┘
                                                 │          │ httpx (async, TTL cache)
                                       SQLAlchemy│          ▼
                                                 ▼    GitHub GraphQL / REST
                                     PostgreSQL / SQLite   LeetCode GraphQL
```

## Components

| Path | Role |
|---|---|
| `backend/app/auth.py` | GitHub OAuth (state cookie for CSRF), signed session cookie, dev login, `current_user` dependency |
| `backend/app/sources/github.py` | Contribution calendar via GraphQL (with token) or public events API (without) |
| `backend/app/sources/leetcode.py` | Solved counts + submission calendar from LeetCode's public GraphQL |
| `backend/app/sources/cache.py` | In-process TTL cache (default 10 min) so refreshes don't hit rate limits |
| `backend/app/risk.py` | Streak, longest streak, week totals, trend line, alerts. No I/O |
| `backend/app/routers/goals.py` | Goal CRUD and daily progress logging |
| `backend/app/routers/dashboard.py` | `/api/me` and `/api/dashboard`, which fetches sources in parallel and runs the risk report |
| `frontend/src/components/` | `Login`, `DashboardPage`, `StreakBanner`, `StatCard`, `Heatmap`, `LeetCodeCard`, `GoalsWidget` |

## Data model

```
users       id · github_login (unique) · avatar_url · leetcode_username · github_token · created_at
goals       id · user_id → users · title · daily_target · created_at
goal_logs   id · goal_id → goals · day · count        UNIQUE(goal_id, day)
```

A goal counts as "done" on a day when `count >= daily_target`. Goal streaks use the same `risk.current_streak` as GitHub and LeetCode.

## Request flow: `GET /api/dashboard?today=2024-06-20`

1. `current_user` verifies the signed session cookie
2. GitHub and LeetCode are fetched concurrently (`asyncio.gather(..., return_exceptions=True)`), each through the TTL cache
3. Failures go into `errors.{github,leetcode}` instead of failing the request
4. Goals with any history are turned into `{day: 1}` maps of done days
5. `risk.report` runs every source and returns alerts (danger → warning → info) plus a summary per source

## Risk rules

| Kind | Level | Fires when |
|---|---|---|
| `streak_ends_today` | danger | streak ≥ 2 days and nothing logged today |
| `flatline` | warning | ≥ 3 idle days after activity in the 2 weeks before |
| `declining` | warning | this week ≤ 60% of last week, and last week had ≥ 5 |
| `projected_stop` | info | a least-squares line over 14 days reaches zero within 7 days |

## API

| Method | Path | Notes |
|---|---|---|
| GET | `/auth/config` | which login buttons to show |
| GET | `/auth/github/login` → `/auth/github/callback` | OAuth flow |
| POST | `/auth/dev-login` | only when `DEV_LOGIN=true` |
| POST | `/auth/logout` | |
| GET / PATCH | `/api/me` | PATCH sets `leetcode_username` |
| GET | `/api/dashboard` | calendars, solved counts, alerts, summaries |
| GET / POST | `/api/goals` | |
| PATCH / DELETE | `/api/goals/{id}` | |
| POST | `/api/goals/{id}/log` | `{"delta": 1}` or `-1` for today |

Interactive docs at `http://localhost:8000/docs`.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
