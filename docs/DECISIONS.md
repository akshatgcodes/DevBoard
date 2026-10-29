# Decisions

### 1. Risk rules as pure functions over `{date: count}`
**Context:** Three different sources (GitHub, LeetCode, goals) need the same streak logic.
**Decision:** `risk.py` has no I/O. Every source is reduced to a date → count map first.
**Why:** One implementation, and the edge cases (midnight grace, quiet weeks, rising trends) are tested with plain dicts.
**Trade-off:** Sources must be converted up front, even if a rule only needs the last 14 days.

### 2. A trend line, not just thresholds
**Context:** "Down 40% this week" fires late, and a single bad day is noise.
**Decision:** Fit a least-squares line over the last 14 days and warn if it reaches zero within 7 days.
**Why:** It catches a steady slide before the weekly comparison does, and it's explainable in one sentence.
**Trade-off:** One huge day early in the window can tilt the slope. The alert is `info`, not `danger`, for that reason.

### 3. The client sends "today"
**Context:** Streaks follow the user's day. The server may be in UTC.
**Decision:** Every request carries `?today=YYYY-MM-DD` from the browser, falling back to the server date.
**Trade-off:** A user could fake their date. That only affects their own dashboard, so it's acceptable.

### 4. Two GitHub data paths
**Context:** The contribution calendar is only available through GraphQL, which needs a token.
**Decision:** With OAuth, use GraphQL (365 days, includes private contributions). Without, use the public events API (~90 days of public pushes).
**Why:** Dev login works with zero setup, and the UI says which source is in use.

### 5. Signed cookie sessions instead of JWT in localStorage
**Decision:** The session is an `HttpOnly` cookie holding a signed user ID (itsdangerous, 30-day expiry). OAuth uses a separate short-lived `state` cookie against CSRF.
**Why:** JavaScript can't read the token, and there's no token refresh to build.
**Trade-off:** Cross-domain deploys need `SameSite=None; Secure` (`CROSS_SITE_COOKIES=true`).

### 6. In-process TTL cache instead of Redis
**Decision:** A dict with timestamps, 10-minute TTL.
**Why:** It's one process with one user per session. Redis would be a second service for no gain.
**Trade-off:** The cache resets on restart and isn't shared between workers.

### 7. `create_all` instead of migrations
**Decision:** Tables are created on startup.
**Why:** Three tables, no production data yet. Alembic is the first thing to add when the schema changes.

### 8. SQLite locally, PostgreSQL in production
**Decision:** `DATABASE_URL` picks the engine; the default is a local SQLite file.
**Why:** `uv sync` and run, nothing else to install. The models use only portable types.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
