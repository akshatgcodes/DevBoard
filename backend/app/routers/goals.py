from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import risk
from app.auth import current_user
from app.db import get_db
from app.models import Goal, GoalLog, User

router = APIRouter(prefix="/api/goals", tags=["goals"])


def today_param(today: date | None = Query(None, description="Client's local date")) -> date:
    """The browser sends its own date so 'today' matches the user's timezone."""
    return today or date.today()


class GoalIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    daily_target: int = Field(1, ge=1, le=100)


class GoalPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    daily_target: int | None = Field(None, ge=1, le=100)


class LogIn(BaseModel):
    delta: int = Field(1, ge=-100, le=100)


def done_days(goal: Goal) -> risk.Counts:
    """A day counts toward the goal streak only if the target was hit."""
    return {log.day: 1 for log in goal.logs if log.count >= goal.daily_target}


def serialize(goal: Goal, today: date) -> dict:
    by_day = {log.day: log.count for log in goal.logs}
    done = done_days(goal)
    return {
        "id": goal.id,
        "title": goal.title,
        "daily_target": goal.daily_target,
        "today_count": by_day.get(today, 0),
        "done_today": today in done,
        "streak": risk.current_streak(done, today),
        # Last 7 days, oldest first, for the mini history dots
        "week": [(today - timedelta(days=i)) in done for i in range(6, -1, -1)],
    }


def _own_goal(db: Session, user: User, goal_id: int) -> Goal:
    goal = db.get(Goal, goal_id)
    if goal is None or goal.user_id != user.id:
        raise HTTPException(404, "Goal not found")
    return goal


@router.get("")
def list_goals(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    today: date = Depends(today_param),
) -> list[dict]:
    goals = db.scalars(select(Goal).where(Goal.user_id == user.id).order_by(Goal.id)).all()
    return [serialize(g, today) for g in goals]


@router.post("", status_code=201)
def create_goal(
    body: GoalIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    today: date = Depends(today_param),
) -> dict:
    goal = Goal(user_id=user.id, title=body.title.strip(), daily_target=body.daily_target)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return serialize(goal, today)


@router.patch("/{goal_id}")
def update_goal(
    goal_id: int,
    body: GoalPatch,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    today: date = Depends(today_param),
) -> dict:
    goal = _own_goal(db, user, goal_id)
    if body.title is not None:
        goal.title = body.title.strip()
    if body.daily_target is not None:
        goal.daily_target = body.daily_target
    db.commit()
    return serialize(goal, today)


@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(_own_goal(db, user, goal_id))
    db.commit()


@router.post("/{goal_id}/log")
def log_progress(
    goal_id: int,
    body: LogIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    today: date = Depends(today_param),
) -> dict:
    goal = _own_goal(db, user, goal_id)
    log = db.scalar(select(GoalLog).where(GoalLog.goal_id == goal.id, GoalLog.day == today))
    if log is None:
        log = GoalLog(goal_id=goal.id, day=today, count=0)
        db.add(log)
    log.count = max(0, log.count + body.delta)
    db.commit()
    db.refresh(goal)
    return serialize(goal, today)
