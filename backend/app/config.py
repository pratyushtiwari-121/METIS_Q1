import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR.parent / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "quantum_security.db"

def _parse_cors_origins() -> list[str]:
    cors_str = os.getenv("CORS_ORIGINS")
    if cors_str:
        import json
        try:
            parsed = json.loads(cors_str)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return [x.strip() for x in cors_str.split(",") if x.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://metis-q1.vercel.app",
    ]

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
