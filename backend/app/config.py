from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
ROOT_DIR = BACKEND_DIR.parent

DATA_PATH = Path(os.getenv("SPREE_DATA_PATH", str(ROOT_DIR / "students.csv")))

_raw_origins = os.getenv("SPREE_CORS_ORIGINS")
if _raw_origins:
    CORS_ORIGINS = [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]
else:
    CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
