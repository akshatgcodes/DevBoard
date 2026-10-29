import os
import tempfile

# Settings are read at import time, so point them at a throwaway DB before importing the app
_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_db.name}"
os.environ["DEV_LOGIN"] = "true"
os.environ["GITHUB_CLIENT_ID"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.sources import cache  # noqa: E402


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    cache.clear()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def logged_in(client):
    assert client.post("/auth/dev-login", json={"username": "octocat"}).status_code == 200
    return client
