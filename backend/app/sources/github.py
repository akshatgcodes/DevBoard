"""GitHub activity as {date: contribution_count}.

With an OAuth token we use the GraphQL contribution calendar (a full year, includes
private contributions the user can see). Without one we fall back to the public events
API, which only covers the last ~90 days of public pushes.
"""

from collections import Counter
from datetime import date, datetime

import httpx

from app.sources.cache import cached

API = "https://api.github.com"

CALENDAR_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


class GitHubError(Exception):
    pass


async def _calendar(login: str, token: str) -> dict[date, int]:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{API}/graphql",
            json={"query": CALENDAR_QUERY, "variables": {"login": login}},
            headers={"Authorization": f"Bearer {token}"},
        )
    if r.status_code != 200:
        raise GitHubError(f"GitHub GraphQL returned {r.status_code}")
    body = r.json()
    user = (body.get("data") or {}).get("user")
    if not user:
        raise GitHubError(f"GitHub user {login!r} not found")
    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {
        date.fromisoformat(d["date"]): d["contributionCount"]
        for w in weeks
        for d in w["contributionDays"]
    }


async def _public_events(login: str) -> dict[date, int]:
    counts: Counter[date] = Counter()
    async with httpx.AsyncClient(timeout=10) as client:
        # The events API caps at 300 events across 3 pages of 100
        for page in (1, 2, 3):
            r = await client.get(
                f"{API}/users/{login}/events/public",
                params={"per_page": 100, "page": page},
                headers={"Accept": "application/vnd.github+json"},
            )
            if r.status_code == 404:
                raise GitHubError(f"GitHub user {login!r} not found")
            if r.status_code != 200:
                raise GitHubError(f"GitHub events API returned {r.status_code}")
            events = r.json()
            for e in events:
                if e["type"] != "PushEvent":
                    continue
                day = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")).date()
                counts[day] += e["payload"].get("size", 1) or 1
            if len(events) < 100:
                break
    return dict(counts)


async def activity(login: str, token: str | None) -> dict[date, int]:
    if token:
        return await cached(f"gh:cal:{login}", lambda: _calendar(login, token))
    return await cached(f"gh:events:{login}", lambda: _public_events(login))
