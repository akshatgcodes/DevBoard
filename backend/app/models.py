from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    github_login: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    leetcode_username: Mapped[str | None] = mapped_column(String(100))
    # OAuth token, used for the GraphQL contribution calendar. Null for dev logins.
    github_token: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    goals: Mapped[list["Goal"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    # How many times per day counts as "done" (e.g. 3 LeetCode problems)
    daily_target: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="goals")
    logs: Mapped[list["GoalLog"]] = relationship(
        back_populates="goal", cascade="all, delete-orphan"
    )


class GoalLog(Base):
    """One row per goal per day; `count` is how much of the target was done that day."""

    __tablename__ = "goal_logs"
    __table_args__ = (UniqueConstraint("goal_id", "day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"), index=True)
    day: Mapped[date] = mapped_column(Date)
    count: Mapped[int] = mapped_column(Integer, default=0)

    goal: Mapped[Goal] = relationship(back_populates="logs")
