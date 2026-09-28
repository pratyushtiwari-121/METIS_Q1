from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.session import engine, Base, SessionLocal
from app.services.seed_data import seed_initial_data
from app.api.dashboard import router as dashboard_router
from app.api.signatures import router as signatures_router
from app.api.verification import router as verification_router
from app.api.attacks import router as attacks_router
from app.api.quantum_circuit import router as quantum_router
from app.api.analytics import router as analytics_router
from app.api.logs import router as logs_router
from app.api.settings import router as settings_router
from app.api.physics_lab import router as physics_lab_router
from app.api.qds import router as qds_router
from app.api.analysis import router as analysis_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database schema
    Base.metadata.create_all(bind=engine)
    # Seed initial demo data
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Quantum Digital Signature Security Educational Simulator API (SIH 2026)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG,
)

# CORS Configuration
_cors_origins = settings.CORS_ORIGINS
_allow_all = "*" in _cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _allow_all else _cors_origins,
    allow_origin_regex=None if _allow_all else r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import RedirectResponse, Response

# Health endpoint
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "simulator": "Qiskit Aer Simulator (Local)",
        "quantum_ready": True
    }

# Root endpoint -> Redirect to interactive API docs
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")

# Favicon handler to avoid 404 in browser
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

# Mount sub-routers
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(signatures_router, prefix=settings.API_PREFIX)
app.include_router(verification_router, prefix=settings.API_PREFIX)
app.include_router(attacks_router, prefix=settings.API_PREFIX)
app.include_router(quantum_router, prefix=settings.API_PREFIX)
app.include_router(analytics_router, prefix=settings.API_PREFIX)
app.include_router(logs_router, prefix=settings.API_PREFIX)
app.include_router(settings_router, prefix=settings.API_PREFIX)
app.include_router(physics_lab_router, prefix=settings.API_PREFIX)
app.include_router(qds_router, prefix=settings.API_PREFIX)
app.include_router(analysis_router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
