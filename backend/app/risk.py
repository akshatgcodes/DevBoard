"""Streak risk: reads the *trend* of daily activity, not just today's number.

Everything here is pure (counts in, alerts out) so it is easy to test and reuse for
GitHub commits, LeetCode solves and custom goals alike.
"""

from dataclasses import asdict, dataclass
from datetime import date, timedelta

Counts = dict[date, int]

# A week counts as "declining" when it does this fraction or less of the previous week
DECLINE_RATIO = 0.6
# Ignore week-over-week drops when last week was this quiet anyway
MIN_WEEK_FOR_TREND = 5
# Days of zero activity before an otherwise-active source counts as flatlined
FLATLINE_DAYS = 3
# Window used to fit the activity trend line
TREND_WINDOW = 14
# Only warn about a projected stop if it is this close
PROJECTION_HORIZON = 7

SEVERITY = {"danger": 0, "warning": 1, "info": 2}


@dataclass
class Alert:
    level: str  # danger | warning | info
    source: str  # "GitHub", "LeetCode", or a goal title
    kind: str  # streak_ends_today | declining | flatline | projected_stop
    message: str


@dataclass
class Summary:
    current_streak: int
    longest_streak: int
    active_today: bool
    this_week: int
    last_week: int
    change_pct: int | None  # None when last week was 0


def _window_sum(counts: Counts, end: date, days: int) -> int:
    return sum(counts.get(end - timedelta(days=i), 0) for i in range(days))


def current_streak(counts: Counts, today: date) -> int:
    """Consecutive active days ending today, or ending yesterday if today is still empty
    (the streak isn't broken until the day is over)."""
    day = today if counts.get(today, 0) > 0 else today - timedelta(days=1)
    streak = 0
    while counts.get(day, 0) > 0:
        streak += 1
        day -= timedelta(days=1)
    return streak


def longest_streak(counts: Counts) -> int:
    best = run = 0
    prev: date | None = None
    for day in sorted(d for d, n in counts.items() if n > 0):
        run = run + 1 if prev and day - prev == timedelta(days=1) else 1
        best = max(best, run)
        prev = day
    return best


def days_since_active(counts: Counts, today: date, limit: int = 365) -> int | None:
    for i in range(limit):
        if counts.get(today - timedelta(days=i), 0) > 0:
            return i
    return None


def projected_days_to_zero(counts: Counts, today: date) -> float | None:
    """Fit a least-squares line through the last TREND_WINDOW days and return how many
    days from today until it reaches zero. None if the trend is flat or rising."""
    ys = [counts.get(today - timedelta(days=TREND_WINDOW - 1 - i), 0) for i in range(TREND_WINDOW)]
    n = len(ys)
    x_mean = (n - 1) / 2
    y_mean = sum(ys) / n
    denom = sum((x - x_mean) ** 2 for x in range(n))
    slope = sum((x - x_mean) * (y - y_mean) for x, y in enumerate(ys)) / denom
    if slope >= 0:
        return None
    today_fit = y_mean + slope * (n - 1 - x_mean)
    if today_fit <= 0:
        return 0.0
    return today_fit / -slope


def summarize(counts: Counts, today: date) -> Summary:
    this_week = _window_sum(counts, today, 7)
    last_week = _window_sum(counts, today - timedelta(days=7), 7)
    change = round((this_week - last_week) / last_week * 100) if last_week else None
    return Summary(
        current_streak=current_streak(counts, today),
        longest_streak=longest_streak(counts),
        active_today=counts.get(today, 0) > 0,
        this_week=this_week,
        last_week=last_week,
        change_pct=change,
    )


def assess(source: str, counts: Counts, today: date, unit: str = "contributions") -> list[Alert]:
    s = summarize(counts, today)
    alerts: list[Alert] = []

    if not s.active_today and s.current_streak >= 2:
        alerts.append(
            Alert(
                "danger",
                source,
                "streak_ends_today",
                f"Your {s.current_streak}-day {source} streak ends at midnight. Go ship something.",
            )
        )

    idle = days_since_active(counts, today)
    recent_history = _window_sum(counts, today - timedelta(days=FLATLINE_DAYS), TREND_WINDOW)
    if idle is not None and idle >= FLATLINE_DAYS and recent_history > 0:
        alerts.append(
            Alert(
                "warning",
                source,
                "flatline",
                f"No {source} {unit} in {idle} days. It was active the two weeks before.",
            )
        )

    if s.last_week >= MIN_WEEK_FOR_TREND and s.this_week <= s.last_week * DECLINE_RATIO:
        alerts.append(
            Alert(
                "warning",
                source,
                "declining",
                f"{source} {unit} down {abs(s.change_pct or 0)}% week-over-week "
                f"({s.last_week} → {s.this_week}).",
            )
        )

    # Only project a stop while still active; flatline already covers the idle case
    if s.active_today or s.current_streak:
        days = projected_days_to_zero(counts, today)
        if days is not None and days <= PROJECTION_HORIZON:
            n = max(1, round(days))
            alerts.append(
                Alert(
                    "info",
                    source,
                    "projected_stop",
                    f"At this pace your {source} activity hits zero in about {n} "
                    f"day{'s' if n != 1 else ''}. Your streak is at risk.",
                )
            )

    return alerts


def report(sources: dict[str, Counts], today: date, units: dict[str, str] | None = None) -> dict:
    units = units or {}
    alerts: list[Alert] = []
    summaries = {}
    for name, counts in sources.items():
        alerts += assess(name, counts, today, units.get(name, "activity"))
        summaries[name] = asdict(summarize(counts, today))
    alerts.sort(key=lambda a: SEVERITY[a.level])
    return {"alerts": [asdict(a) for a in alerts], "summaries": summaries}
