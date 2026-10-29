# Deploy

DevBoard is **not deployed yet**. This is the intended setup.

| Part | Platform |
|---|---|
| Frontend | Vercel (`frontend/`, build `npm run build`, output `dist`) |
| API | Render web service (`backend/`, start `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`) |
| Database | Neon PostgreSQL |

## Environment

On the API:

- `DATABASE_URL=postgresql+psycopg://…` (Neon connection string)
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` from a production OAuth app
- `OAUTH_REDIRECT_URL=https://<api-host>/auth/github/callback`
- `FRONTEND_URL=https://<frontend-host>`
- `SESSION_SECRET` set to a long random value
- `CROSS_SITE_COOKIES=true` (frontend and API on different domains)
- `DEV_LOGIN` unset

On the frontend: `VITE_API_URL=https://<api-host>`.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
