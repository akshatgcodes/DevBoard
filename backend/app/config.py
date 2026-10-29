from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./devboard.db"
    github_client_id: str = ""
    github_client_secret: str = ""
    session_secret: str = "dev-insecure-secret"
    frontend_url: str = "http://localhost:5173"
    oauth_redirect_url: str = "http://localhost:8000/auth/github/callback"
    # True in production when frontend and API live on different domains:
    # the session cookie then needs SameSite=None; Secure
    cross_site_cookies: bool = False
    dev_login: bool = False
    # Seconds to keep GitHub/LeetCode responses before refetching
    cache_ttl: int = 600


settings = Settings()
