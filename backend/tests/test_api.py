from datetime import date, timedelta

from app.sources import github, leetcode

TODAY = date(2024, 6, 20)
Q = {"today": TODAY.isoformat()}


def test_requires_login(client):
    assert client.get("/api/me").status_code == 401
    assert client.get("/api/goals").status_code == 401


def test_tampered_session_rejected(client):
    client.cookies.set("devboard_session", "forged")
    assert client.get("/api/me").status_code == 401


def test_auth_config_without_oauth(client):
    assert client.get("/auth/config").json() == {"github": False, "dev_login": True}
    assert client.get("/auth/github/login", follow_redirects=False).status_code == 503


def test_dev_login_and_me(logged_in):
    me = logged_in.get("/api/me").json()
    assert me["login"] == "octocat" and me["oauth"] is False


def test_dev_login_rejects_bad_username(client):
    assert client.post("/auth/dev-login", json={"username": "a/b"}).status_code == 422


def test_goal_crud_and_log(logged_in):
    goal = logged_in.post(
        "/api/goals", json={"title": "Solve 2 problems", "daily_target": 2}, params=Q
    ).json()
    gid = goal["id"]
    assert goal["today_count"] == 0 and not goal["done_today"]

    logged_in.post(f"/api/goals/{gid}/log", json={"delta": 1}, params=Q)
    goal = logged_in.post(f"/api/goals/{gid}/log", json={"delta": 1}, params=Q).json()
    assert goal["today_count"] == 2 and goal["done_today"] and goal["streak"] == 1
    assert goal["week"][-1] is True

    # Count never goes below zero
    goal = logged_in.post(f"/api/goals/{gid}/log", json={"delta": -5}, params=Q).json()
    assert goal["today_count"] == 0

    goal = logged_in.patch(f"/api/goals/{gid}", json={"title": "Solve 3"}, params=Q).json()
    assert goal["title"] == "Solve 3"

    assert logged_in.delete(f"/api/goals/{gid}").status_code == 204
    assert logged_in.get("/api/goals", params=Q).json() == []


def test_goal_streak_across_days(logged_in):
    gid = logged_in.post("/api/goals", json={"title": "Read"}).json()["id"]
    for ago in (2, 1):
        day = (TODAY - timedelta(days=ago)).isoformat()
        logged_in.post(f"/api/goals/{gid}/log", json={"delta": 1}, params={"today": day})
    goal = logged_in.get("/api/goals", params=Q).json()[0]
    assert goal["streak"] == 2 and not goal["done_today"]


def test_cannot_touch_other_users_goal(client):
    client.post("/auth/dev-login", json={"username": "alice"})
    gid = client.post("/api/goals", json={"title": "Alice goal"}).json()["id"]
    client.post("/auth/dev-login", json={"username": "bob"})
    assert client.post(f"/api/goals/{gid}/log", json={"delta": 1}).status_code == 404
    assert client.delete(f"/api/goals/{gid}").status_code == 404


def test_dashboard_combines_sources(logged_in, monkeypatch):
    async def fake_gh(login, token):
        # Active yesterday and the day before, nothing today → streak ends tonight
        return {TODAY - timedelta(days=1): 3, TODAY - timedelta(days=2): 1}

    async def fake_lc(username):
        return {
            "solved": {"all": 120, "easy": 60, "medium": 50, "hard": 10},
            "calendar": {TODAY: 2},
        }

    monkeypatch.setattr(github, "activity", fake_gh)
    monkeypatch.setattr(leetcode, "stats", fake_lc)
    logged_in.patch("/api/me", json={"leetcode_username": "octo_lc"})

    data = logged_in.get("/api/dashboard", params=Q).json()
    assert data["errors"] == {}
    assert len(data["github"]["calendar"]) == 365
    assert data["github"]["calendar"][-1] == {"date": TODAY.isoformat(), "count": 0}
    assert data["leetcode"]["solved"]["all"] == 120
    assert data["alerts"][0]["kind"] == "streak_ends_today"
    assert data["summaries"]["GitHub"]["current_streak"] == 2


def test_dashboard_survives_source_failure(logged_in, monkeypatch):
    async def broken(login, token):
        raise github.GitHubError("GitHub events API returned 403")

    monkeypatch.setattr(github, "activity", broken)
    data = logged_in.get("/api/dashboard", params=Q).json()
    assert data["github"] is None
    assert "403" in data["errors"]["github"]
    assert data["leetcode"] is None  # no username set
