import type { Site } from "./types";

export const site: Site = {
  name: "DevBoard",
  letter: "D",
  title: "DevBoard — a warning before your streak breaks",
  description:
    "Your GitHub commits, LeetCode solves and daily goals on one page, with a warning before a streak breaks.",
  meta: ["live", "GitHub + LeetCode + goals", "GPLv3"],
  headline: ["A warning", "before your streak breaks."],
  intro:
    "Most developer dashboards show today's numbers and stop there. DevBoard reads the trend: it pulls your GitHub contribution calendar and LeetCode history, tracks your own daily goals, and puts a banner on top when the pattern says you're slipping.",
  primary: { label: "Open DevBoard", href: "/app/" },
  repo: "https://github.com/akshatgcodes/DevBoard",
  note: "Log in with GitHub (read-only `read:user` scope). LeetCode only needs a public username.",
  xfactor: {
    title: "It warns you before, not after.",
    intro:
      "Four rules run over every source, GitHub, LeetCode and each of your goals, and the most urgent one goes on top.",
    features: [
      {
        icon: "🔥",
        title: "Streak ends today",
        body: "A streak that is alive but has nothing for today gets a red banner: \"Your 9-day GitHub streak ends at midnight.\" It uses your local date, which the browser sends, so it doesn't fire at the server's midnight.",
      },
      {
        icon: "📉",
        title: "Decline and flatline",
        body: "This week against last week, and a quiet spell after a busy fortnight: \"GitHub contributions down 46% week-over-week (28 → 15).\"",
      },
      {
        icon: "⏳",
        title: "Trend to zero",
        body: "A least-squares line over the last two weeks projects when activity hits zero: \"At this pace your LeetCode activity hits zero in about 2 days.\"",
      },
    ],
  },
  preview: {
    intro:
      "Streak cards with week-over-week change, a year of GitHub activity, LeetCode solves by difficulty and daily goals with their own streaks. Light and dark follow your system.",
    shots: [
      { src: "/shots/dashboard.png", alt: "DevBoard dashboard with two risk banners, streak cards, heatmaps and daily goals", caption: "Dashboard" },
      { src: "/shots/dark.png", alt: "The same dashboard in dark mode", caption: "Dark mode" },
    ],
  },
  stack: ["React 19", "TypeScript", "Vite", "FastAPI", "SQLAlchemy 2", "httpx", "PostgreSQL", "GitHub OAuth", "GitHub GraphQL", "LeetCode GraphQL", "pytest", "Vitest"],
  concepts: [
    { title: "Pure risk engine", body: "`risk.py` takes `{date: count}` and returns alerts. No I/O, so one set of rules covers every source and the tests need no mocks." },
    { title: "The user's today", body: "Every API call carries the browser's local date, so a streak doesn't \"break\" at 5:30 am for someone in India." },
    { title: "Sources fail alone", body: "GitHub and LeetCode are fetched in parallel; if one is down, only its card shows an error." },
    { title: "Short-lived cache", body: "Upstream responses are kept for ten minutes, so refreshing the page doesn't hit GitHub's or LeetCode's rate limits." },
    { title: "Hand-rolled heatmap", body: "An SVG grid with levels from the data's own quartiles, so a quiet year and a busy year both show contrast." },
    { title: "Signed session cookie", body: "GitHub OAuth with a state check, then an `HttpOnly` cookie signed with itsdangerous. The token never reaches the browser." },
  ],
  run: {
    title: "Run your own",
    intro: "No OAuth app needed locally: with `DEV_LOGIN=true` you can open the dashboard as any public GitHub username.",
    blocks: [
      {
        title: "API",
        steps: [
          { text: "Install and configure:", cmd: "cd backend && uv sync\ncp .env.example .env" },
          { text: "Start it on port 8000:", cmd: "uv run uvicorn app.main:app --reload" },
        ],
      },
      {
        title: "App",
        steps: [
          { text: "Install and start Vite:", cmd: "cd frontend && npm install\nnpm run dev" },
          { text: "Open it:", cmd: "http://localhost:5173" },
        ],
      },
    ],
  },
  tagline: "GitHub, LeetCode and goals, with streak warnings.",
};
