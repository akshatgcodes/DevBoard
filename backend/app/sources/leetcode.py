"""LeetCode stats from the public GraphQL endpoint (no auth needed)."""

import json
from datetime import UTC, date, datetime

import httpx

from app.sources.cache import cached

URL = "https://leetcode.com/graphql"

QUERY = """
query($username: String!) {
  matchedUser(username: $username) {
    submitStatsGlobal { acSubmissionNum { difficulty count } }
    userCalendar { submissionCalendar }
  }
}
"""


class LeetCodeError(Exception):
    pass


async def _fetch(username: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            URL,
            json={"query": QUERY, "variables": {"username": username}},
            headers={"Referer": "https://leetcode.com", "Content-Type": "application/json"},
        )
    if r.status_code != 200:
        raise LeetCodeError(f"LeetCode returned {r.status_code}")
    user = (r.json().get("data") or {}).get("matchedUser")
    if not user:
        raise LeetCodeError(f"LeetCode user {username!r} not found")

    solved = {
        row["difficulty"].lower(): row["count"]
        for row in user["submitStatsGlobal"]["acSubmissionNum"]
    }
    # submissionCalendar is a JSON string of {unix_timestamp: submissions_that_day}
    raw = json.loads(user["userCalendar"]["submissionCalendar"] or "{}")
    calendar = {
        datetime.fromtimestamp(int(ts), tz=UTC).date(): n for ts, n in raw.items()
    }
    return {"solved": solved, "calendar": calendar}


async def stats(username: str) -> dict[str, dict]:
    """Returns {"solved": {"all","easy","medium","hard"}, "calendar": {date: count}}."""
    return await cached(f"lc:{username}", lambda: _fetch(username))
