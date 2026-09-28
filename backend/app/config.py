import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR.parent / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "quantum_security.db"

def _parse_cors_origins() -> list[str]:
    default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://metis-q1.vercel.app",
    ]
    cors_str = os.getenv("CORS_ORIGINS")
    if not cors_str:
        return default_origins

    cors_str = cors_str.strip()
    if cors_str in ("*", '"*"', "'*'"):
        return ["*"]

    import json
    try:
        parsed = json.loads(cors_str)
        if isinstance(parsed, list):
            res = [str(x).strip().rstrip("/") for x in parsed if str(x).strip()]
            for d in default_origins:
                if d not in res and "*" not in res:
                    res.append(d)
            return res
        elif isinstance(parsed, str):
            cors_str = parsed
    except Exception:
        pass

    clean_str = cors_str.strip("[]() ")
    items = []
    for item in clean_str.split(","):
        cleaned = item.strip().strip("'\"").rstrip("/")
        if cleaned:
            items.append(cleaned)

    for d in default_origins:
        if d not in items and "*" not in items:
            items.append(d)

    return items or ["*"]

class Settings(BaseModel):
    PROJECT_NAME: str = "Quantum Digital Signature Security"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    CORS_ORIGINS: list[str] = _parse_cors_origins()
    DEFAULT_SHOTS: int = 1024
    DEFAULT_VERIFICATION_THRESHOLD: float = 0.100  # max allowable TVD
    DEFAULT_FIDELITY_THRESHOLD: float = 0.850     # min allowable state fidelity
    REPLAY_WINDOW_SECONDS: int = 3600             # 1 hour validity

settings = Settings()
