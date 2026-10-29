import asyncio
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import risk
from app.auth import current_user
from app.db import get_db
from app.models import Goal, User
from app.routers.goals import done_days, today_param
from app.sources import github, leetcode

router = APIRouter(prefix="/api", tags=["dashboard"])

# Days of history sent to the heatmap
CALENDAR_DAYS = 365


def _calendar(counts: risk.Counts, today: date) -> list[dict]:
    start = today - timedelta(days=CALENDAR_DAYS - 1)
    return [
        {
            "date": (start + timedelta(days=i)).isoformat(),
            "count": counts.get(start + timedelta(days=i), 0),
        }
        for i in range(CALENDAR_DAYS)
    ]


@router.get("/me")
def me(user: User = Depends(current_user)) -> dict:
    return {
        "login": user.github_login,
        "avatar_url": user.avatar_url,
        "leetcode_username": user.leetcode_username,
        "oauth": user.github_token is not None,
    }


class MePatch(BaseModel):
    leetcode_username: str | None = Field(None, max_length=100, pattern=r"^[A-Za-z0-9_-]*$")


@router.patch("/me")
def update_me(body: MePatch, user: User = Depends(current_user), db: Session = Depends(get_db)):
    user.leetcode_username = body.leetcode_username or None
    db.commit()
    return me(user)


@router.get("/dashboard")
async def dashboard(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    today: date = Depends(today_param),
) -> dict:
    async def gh():
        return await github.activity(user.github_login, user.github_token)

    async def lc():
        if not user.leetcode_username:
            return None
        return await leetcode.stats(user.leetcode_username)

    # Fetch both in parallel; one source failing must not blank the whole dashboard
    gh_result, lc_result = await asyncio.gather(gh(), lc(), return_exceptions=True)

    sources: dict[str, risk.Counts] = {}
    units: dict[str, str] = {}
    out: dict = {"github": None, "leetcode": None, "errors": {}}

    if isinstance(gh_result, Exception):
        out["errors"]["github"] = str(gh_result)
    else:
        sources["GitHub"], units["GitHub"] = gh_result, "contributions"
        out["github"] = {
            "calendar": _calendar(gh_result, today),
            "source": "graphql" if user.github_token else "public_events",
        }

    if isinstance(lc_result, Exception):
        out["errors"]["leetcode"] = str(lc_result)
    elif lc_result is not None:
        sources["LeetCode"], units["LeetCode"] = lc_result["calendar"], "submissions"
        out["leetcode"] = {
            "username": user.leetcode_username,
            "solved": lc_result["solved"],
            "calendar": _calendar(lc_result["calendar"], today),
        }

    goals = db.scalars(select(Goal).where(Goal.user_id == user.id)).all()
    for g in goals:
        # Brand-new goals have no history to judge yet
        if g.logs:
            sources[g.title], units[g.title] = done_days(g), "check-ins"

    out |= risk.report(sources, today, units)
    return out
