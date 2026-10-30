"""Vercel entry point: the FastAPI app from backend/, served at /api and /auth (see vercel.json)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.main import app  # noqa: E402

__all__ = ["app"]
