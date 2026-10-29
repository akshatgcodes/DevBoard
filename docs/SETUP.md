# Setup

## Requirements

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Node 18+ (22 recommended)
- Optional: PostgreSQL (SQLite is used if `DATABASE_URL` is unset)

## Backend

```bash
cd backend
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload     # http://localhost:8000/docs
```

## Frontend

```bash
cd frontend
npm install
npm run dev                              # http://localhost:5173
```

Vite proxies `/api` and `/auth` to `localhost:8000`, so the session cookie works without CORS setup.

## Environment variables (`backend/.env`)

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./devboard.db` | e.g. `postgresql+psycopg://user:pass@host:5432/devboard` |
| `GITHUB_CLIENT_ID` | empty | OAuth app client ID. Empty hides the GitHub button |
| `GITHUB_CLIENT_SECRET` | empty | OAuth app secret |
| `OAUTH_REDIRECT_URL` | `http://localhost:8000/auth/github/callback` | must match the OAuth app's callback URL |
| `SESSION_SECRET` | insecure dev value | signs session cookies. Use a long random string |
| `FRONTEND_URL` | `http://localhost:5173` | CORS origin and post-login redirect |
| `DEV_LOGIN` | `false` | `true` allows logging in as any username. Local only |
| `CROSS_SITE_COOKIES` | `false` | `true` when frontend and API are on different domains |
| `CACHE_TTL` | `600` | seconds to cache GitHub/LeetCode responses |

Frontend (`frontend/.env`, optional): `VITE_API_URL` points the app at an API on another origin.

## GitHub OAuth app

1. GitHub → Settings → Developer settings → OAuth Apps → New
2. Homepage: `http://localhost:5173`, callback: `http://localhost:8000/auth/github/callback`
3. Put the client ID and secret in `backend/.env`

## Checks

```bash
cd backend && uv run ruff check . && uv run pytest
cd frontend && npm run build
```

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
