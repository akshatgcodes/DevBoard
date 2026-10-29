from datetime import date, timedelta

from app import risk

TODAY = date(2024, 6, 20)


def days(*offsets_and_counts: tuple[int, int]) -> dict[date, int]:
    """Build counts from (days_ago, count) pairs."""
    return {TODAY - timedelta(days=ago): n for ago, n in offsets_and_counts}


def kinds(alerts):
    return {a.kind for a in alerts}


def test_streak_counts_today():
    assert risk.current_streak(days((0, 1), (1, 2), (2, 1)), TODAY) == 3


def test_streak_survives_until_midnight():
    # Nothing today yet, but yesterday + the day before were active
    assert risk.current_streak(days((1, 1), (2, 1)), TODAY) == 2


def test_streak_broken_by_gap():
    assert risk.current_streak(days((0, 1), (2, 1), (3, 1)), TODAY) == 1


def test_longest_streak():
    assert risk.longest_streak(days((0, 1), (5, 1), (6, 1), (7, 1), (10, 1))) == 3


def test_streak_ends_today_alert():
    alerts = risk.assess("GitHub", days((1, 3), (2, 2), (3, 1)), TODAY)
    assert "streak_ends_today" in kinds(alerts)
    assert alerts[0].level == "danger"


def test_no_streak_alert_when_active_today():
    alerts = risk.assess("GitHub", days((0, 1), (1, 1), (2, 1)), TODAY)
    assert "streak_ends_today" not in kinds(alerts)


def test_declining_week_over_week():
    last_week = [(ago, 3) for ago in range(7, 14)]  # 21
    this_week = [(0, 1), (2, 1), (4, 2)]  # 4
    alerts = risk.assess("GitHub", days(*last_week, *this_week), TODAY)
    declining = next(a for a in alerts if a.kind == "declining")
    assert "81%" in declining.message


def test_quiet_last_week_is_not_a_decline():
    alerts = risk.assess("GitHub", days((8, 1), (9, 1), (0, 0)), TODAY)
    assert "declining" not in kinds(alerts)


def test_flatline():
    alerts = risk.assess("LeetCode", days((4, 2), (6, 1), (9, 3)), TODAY, unit="solves")
    flat = next(a for a in alerts if a.kind == "flatline")
    assert "4 days" in flat.message


def test_projected_stop_on_steady_decline():
    # 13 → 1 over two weeks, still active today
    counts = days(*[(ago, ago + 1) for ago in range(14)])
    alerts = risk.assess("GitHub", counts, TODAY)
    assert "projected_stop" in kinds(alerts)


def test_rising_trend_has_no_projection():
    counts = days(*[(ago, 14 - ago) for ago in range(14)])
    assert risk.projected_days_to_zero(counts, TODAY) is None


def test_healthy_activity_has_no_alerts():
    counts = days(*[(ago, 2) for ago in range(30)])
    assert risk.assess("GitHub", counts, TODAY) == []


def test_report_sorts_danger_first():
    out = risk.report(
        {"LeetCode": days((4, 2), (6, 1)), "GitHub": days((1, 1), (2, 1))}, TODAY
    )
    assert out["alerts"][0]["level"] == "danger"
    assert set(out["summaries"]) == {"LeetCode", "GitHub"}
