from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Setting
from app.schemas.schemas import SystemSettings

router = APIRouter(prefix="/settings", tags=["Settings"])

DEFAULT_SETTINGS_MAP = {
    "app_name": "Quantum Digital Signature Security",
    "theme": "dark-quantum",
    "language": "en",
    "timezone": "Asia/Kolkata",
    "default_shots": "1024",
    "default_qubits": "2",
    "simulator_backend": "Qiskit Aer Simulator (Local)",
    "measurement_basis": "Computational (Z-basis)",
    "verification_threshold": "0.100",
    "fidelity_threshold": "0.850",
    "max_verification_attempts": "5",
    "replay_protection": "true",
    "attack_detection_sensitivity": "High",
    "enable_logging": "true",
    "log_retention_days": "30",
    "security_alerts": "true",
    "alert_on_attack": "true",
    "alert_on_verification_failure": "true",
    "noise_model_enabled": "false",
    "debug_mode": "false",
    "simulation_seed": "42"
}

@router.get("", response_model=SystemSettings)
def get_settings(db: Session = Depends(get_db)):
    settings_records = db.query(Setting).all()
    cfg_dict = dict(DEFAULT_SETTINGS_MAP)

    for r in settings_records:
        cfg_dict[r.key] = r.value

    return SystemSettings(
        app_name=cfg_dict.get("app_name", "Quantum Digital Signature Security"),
        theme=cfg_dict.get("theme", "dark-quantum"),
        language=cfg_dict.get("language", "en"),
        timezone=cfg_dict.get("timezone", "Asia/Kolkata"),
        default_shots=int(cfg_dict.get("default_shots", 1024)),
        default_qubits=int(cfg_dict.get("default_qubits", 2)),
        simulator_backend=cfg_dict.get("simulator_backend", "Qiskit Aer Simulator (Local)"),
        measurement_basis=cfg_dict.get("measurement_basis", "Computational (Z-basis)"),
        verification_threshold=float(cfg_dict.get("verification_threshold", 0.100)),
        fidelity_threshold=float(cfg_dict.get("fidelity_threshold", 0.850)),
        max_verification_attempts=int(cfg_dict.get("max_verification_attempts", 5)),
        replay_protection=str(cfg_dict.get("replay_protection", "true")).lower() == "true",
        attack_detection_sensitivity=cfg_dict.get("attack_detection_sensitivity", "High"),
        enable_logging=str(cfg_dict.get("enable_logging", "true")).lower() == "true",
        log_retention_days=int(cfg_dict.get("log_retention_days", 30)),
        security_alerts=str(cfg_dict.get("security_alerts", "true")).lower() == "true",
        alert_on_attack=str(cfg_dict.get("alert_on_attack", "true")).lower() == "true",
        alert_on_verification_failure=str(cfg_dict.get("alert_on_verification_failure", "true")).lower() == "true",
        noise_model_enabled=str(cfg_dict.get("noise_model_enabled", "false")).lower() == "true",
        debug_mode=str(cfg_dict.get("debug_mode", "false")).lower() == "true",
        simulation_seed=int(cfg_dict.get("simulation_seed", 42)) if cfg_dict.get("simulation_seed") else None
    )

@router.put("", response_model=SystemSettings)
def update_settings(new_settings: SystemSettings, db: Session = Depends(get_db)):
    data = new_settings.model_dump()
    for k, v in data.items():
        str_val = str(v)
        rec = db.query(Setting).filter(Setting.key == k).first()
        if rec:
            rec.value = str_val
        else:
            db.add(Setting(key=k, value=str_val, description=f"Setting for {k}"))

    db.commit()
    return get_settings(db)

@router.post("/reset", response_model=SystemSettings)
def reset_settings(db: Session = Depends(get_db)):
    for k, v in DEFAULT_SETTINGS_MAP.items():
        rec = db.query(Setting).filter(Setting.key == k).first()
        if rec:
            rec.value = v
        else:
            db.add(Setting(key=k, value=v, description=f"Setting for {k}"))

    db.commit()
    return get_settings(db)
