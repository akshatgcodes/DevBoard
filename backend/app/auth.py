import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from itsdangerous import BadSignature, URLSafeTimedSerializer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

SESSION_COOKIE = "devboard_session"
STATE_COOKIE = "devboard_oauth_state"
SESSION_MAX_AGE = 60 * 60 * 24 * 30

signer = URLSafeTimedSerializer(settings.session_secret, salt="devboard-session")


def _cookie_args() -> dict:
    if settings.cross_site_cookies:
        return {"httponly": True, "samesite": "none", "secure": True}
    return {"httponly": True, "samesite": "lax"}


def _start_session(response: Response, user: User) -> None:
    response.set_cookie(
        SESSION_COOKIE, signer.dumps(user.id), max_age=SESSION_MAX_AGE, **_cookie_args()
    )


def _upsert_user(db: Session, login: str, avatar_url: str | None, token: str | None) -> User:
    user = db.scalar(select(User).where(User.github_login == login))
    if user is None:
        user = User(github_login=login)
        db.add(user)
    user.avatar_url = avatar_url
    if token is not None:
        user.github_token = token
    db.commit()
    return user


def current_user(
    session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    db: Session = Depends(get_db),
) -> User:
    if not session:
        raise HTTPException(401, "Not logged in")
    try:
        user_id = signer.loads(session, max_age=SESSION_MAX_AGE)
    except BadSignature as e:
        raise HTTPException(401, "Invalid session") from e
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(401, "User no longer exists")
    return user


@router.get("/config")
def auth_config() -> dict:
    """Tells the login screen which buttons to show."""
    return {"github": bool(settings.github_client_id), "dev_login": settings.dev_login}


@router.get("/github/login")
def github_login() -> RedirectResponse:
    if not settings.github_client_id:
        raise HTTPException(503, "GitHub OAuth is not configured (GITHUB_CLIENT_ID missing)")
    state = secrets.token_urlsafe(24)
    query = urlencode(
        {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.oauth_redirect_url,
            "scope": "read:user",
            "state": state,
        }
    )
    response = RedirectResponse(f"https://github.com/login/oauth/authorize?{query}")
    # The state cookie ties the callback to this browser (CSRF protection)
    response.set_cookie(STATE_COOKIE, state, max_age=600, **_cookie_args())
    return response


@router.get("/github/callback")
async def github_callback(
    code: str,
    state: str,
    saved_state: str | None = Cookie(default=None, alias=STATE_COOKIE),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    if not saved_state or not secrets.compare_digest(state, saved_state):
        raise HTTPException(400, "OAuth state mismatch. Try logging in again.")

    async with httpx.AsyncClient(timeout=10) as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.oauth_redirect_url,
            },
            headers={"Accept": "application/json"},
        )
        token = token_res.json().get("access_token")
        if not token:
            raise HTTPException(400, "GitHub did not return an access token")
        me = await client.get(
            "https://api.github.com/user", headers={"Authorization": f"Bearer {token}"}
        )
    me.raise_for_status()
    profile = me.json()

    user = _upsert_user(db, profile["login"], profile.get("avatar_url"), token)
    response = RedirectResponse(settings.frontend_url)
    _start_session(response, user)
    response.delete_cookie(STATE_COOKIE)
    return response


class DevLogin(BaseModel):
    username: str = Field(min_length=1, max_length=39, pattern=r"^[A-Za-z0-9-]+$")


@router.post("/dev-login")
def dev_login(body: DevLogin, response: Response, db: Session = Depends(get_db)) -> dict:
    """Log in as any GitHub username without OAuth. Uses the public events API for data."""
    if not settings.dev_login:
        raise HTTPException(404)
    user = _upsert_user(db, body.username, f"https://github.com/{body.username}.png", None)
    _start_session(response, user)
    return {"ok": True}


@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(SESSION_COOKIE, **_cookie_args())
    return {"ok": True}
