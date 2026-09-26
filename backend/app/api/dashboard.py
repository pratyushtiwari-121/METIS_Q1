import json
import psutil
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.database.models import Signature, Verification, Attack, Log, QuantumCircuitRecord
from app.schemas.schemas import DashboardSummaryResponse, SystemResourceMetrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_sigs = db.query(Signature).count()
    total_verifications = db.query(Verification).count()
    verified_legit = db.query(Verification).filter(Verification.decision == "LEGITIMATE").count()
    total_attacks = db.query(Attack).count()
    detected_attacks = db.query(Attack).filter(Attack.decision.like("%ATTACK%")).count()

    # Dynamic success rate & detection rate
    success_rate = round((verified_legit / total_verifications * 100) if total_verifications > 0 else 100.0, 1)
    detection_rate = round((detected_attacks / total_attacks * 100) if total_attacks > 0 else 100.0, 1)

    # Dynamic signature trend % (e.g. proportion of signatures created in last 24h vs older)
    now_utc = datetime.now(timezone.utc)
    recent_cutoff = now_utc - timedelta(hours=24)
    recent_sigs = db.query(Signature).filter(Signature.timestamp >= recent_cutoff).count()
    signatures_trend_pct = round((recent_sigs / max(1, total_sigs)) * 100, 1) if total_sigs > 0 else 0.0

    # Latest verification or attack result
    latest_ver = db.query(Verification).order_by(desc(Verification.timestamp)).first()
    latest_attack = db.query(Attack).order_by(desc(Attack.timestamp)).first()
    latest_sig = db.query(Signature).order_by(desc(Signature.timestamp)).first()

    latest_result = None
    if latest_attack and (not latest_ver or latest_attack.timestamp >= latest_ver.timestamp):
        is_attack_threat = (
            latest_attack.decision != "LEGITIMATE"
            and latest_attack.threat_score >= 0.30
            and "no attack" not in (latest_attack.attack_type or "").lower()
        )
        threat_label = (
            "Low" if latest_attack.threat_score < 0.30
            else ("Medium" if latest_attack.threat_score < 0.60 else "High")
        )
        
        if is_attack_threat:
            title = f"{latest_attack.attack_type} Detected" if latest_attack.attack_type else "Attack Detected"
            status_text = f"Quantum state deviation detected: {latest_attack.attack_type} intercepted signature."
        else:
            title = "No Attack (Clean Channel Verified)" if "no attack" in (latest_attack.attack_type or "").lower() else "Signature Verified"
            status_text = "Clean quantum transmission verified: Authentic state with zero eavesdropping."

        latest_result = {
            "type": "attack_sim" if is_attack_threat else "baseline",
            "title": title,
            "message_id": latest_attack.signature_id or (latest_sig.signature_id if latest_sig else "QSIG-LIVE-001"),
            "verification_fidelity": latest_attack.fidelity,
            "measurement_deviation": latest_attack.deviation,
            "threat_score": f"{latest_attack.threat_score:.2f} ({threat_label})",
            "final_decision": latest_attack.decision,
            "status": status_text,
            "is_threat": is_attack_threat
        }
    elif latest_ver:
        is_ver_threat = latest_ver.decision != "LEGITIMATE" or latest_ver.threat_score >= 0.30
        threat_label = (
            "Low" if latest_ver.threat_score < 0.30
            else ("Medium" if latest_ver.threat_score < 0.60 else "High")
        )
        latest_result = {
            "type": "verification",
            "title": "Attack Detected" if is_ver_threat else "Signature Verified",
            "message_id": latest_ver.signature_id,
            "verification_fidelity": latest_ver.fidelity,
            "measurement_deviation": latest_ver.deviation,
            "threat_score": f"{latest_ver.threat_score:.2f} ({threat_label})",
            "final_decision": latest_ver.decision,
            "status": "Statistical tampering detected during multi-basis measurement." if is_ver_threat else "The message signature is authentic and untampered.",
            "is_threat": is_ver_threat
        }
    elif latest_sig:
        latest_result = {
            "type": "signature",
            "title": "Signature Active",
            "message_id": latest_sig.signature_id,
            "verification_fidelity": latest_sig.fidelity,
            "measurement_deviation": 0.00,
            "threat_score": "0.00 (Low)",
            "final_decision": "LEGITIMATE",
            "status": "Live quantum state ready for secure transmission and verification.",
            "is_threat": False
        }
    else:
        latest_result = {
            "type": "system",
            "title": "System Initialized",
            "message_id": "QSIG-AER-READY",
            "verification_fidelity": 1.0,
            "measurement_deviation": 0.0,
            "threat_score": "0.00 (Low)",
            "final_decision": "LEGITIMATE",
            "status": "Quantum Aer Simulator is online and ready for signature generation.",
            "is_threat": False
        }

    # Measurement Distribution (from latest verification, latest attack, or latest signature)
    meas_dist = None
    if latest_ver and latest_ver.expected_distribution and latest_ver.observed_distribution:
        try:
            exp_dist = json.loads(latest_ver.expected_distribution)
            obs_dist = json.loads(latest_ver.observed_distribution)
            meas_dist = {
                "p0_exp": exp_dist.get("0", 0.50),
                "p0_obs": obs_dist.get("0", 0.50),
                "p1_exp": exp_dist.get("1", 0.50),
                "p1_obs": obs_dist.get("1", 0.50)
            }
        except Exception:
            pass

    if not meas_dist and latest_attack and latest_attack.expected_distribution and latest_attack.observed_distribution:
        try:
            exp_dist = json.loads(latest_attack.expected_distribution)
            obs_dist = json.loads(latest_attack.observed_distribution)
            meas_dist = {
                "p0_exp": exp_dist.get("0", 0.50),
                "p0_obs": obs_dist.get("0", 0.50),
                "p1_exp": exp_dist.get("1", 0.50),
                "p1_obs": obs_dist.get("1", 0.50)
            }
        except Exception:
            pass

    if not meas_dist and latest_sig and latest_sig.measurement_counts:
        try:
            counts = json.loads(latest_sig.measurement_counts)
            total = max(1, sum(counts.values()))
            p0 = round(counts.get("0", 0) / total, 4)
            p1 = round(counts.get("1", 0) / total, 4)
            meas_dist = {
                "p0_exp": p0,
                "p0_obs": p0,
                "p1_exp": p1,
                "p1_obs": p1
            }
        except Exception:
            pass

    if not meas_dist:
        meas_dist = {
            "p0_exp": 0.50,
            "p0_obs": 0.50,
            "p1_exp": 0.50,
            "p1_obs": 0.50
        }

    # Dynamic Threat Detection Trend (computed from real timestamp progression)
    all_events = []
    for v in db.query(Verification).all():
        if v.timestamp:
            all_events.append({
                "time": v.timestamp,
                "is_attack": v.decision != "LEGITIMATE"
            })
    for a in db.query(Attack).all():
        if a.timestamp:
            all_events.append({
                "time": a.timestamp,
                "is_attack": a.decision.upper() != "LEGITIMATE" and "no attack" not in (a.attack_type or "").lower()
            })

    all_events.sort(key=lambda x: x["time"])

    # Build 7 dynamic time points based on cumulative activity or time window
    threat_trend = []
    if all_events:
        total_ev = len(all_events)
        step = max(1, total_ev // 6)
        checkpoints = [all_events[min(i * step, total_ev - 1)] for i in range(6)]
        checkpoints.append(all_events[-1])
        
        for idx, pt in enumerate(checkpoints):
            pt_time = pt["time"]
            t_str = pt_time.strftime("%H:%M") if idx < 6 else "Now"
            # Count events up to this checkpoint
            legit_count = sum(1 for e in all_events if e["time"] <= pt_time and not e["is_attack"])
            attack_count = sum(1 for e in all_events if e["time"] <= pt_time and e["is_attack"])
            threat_trend.append({
                "time": t_str,
                "legitimate": legit_count,
                "attacks": attack_count
            })
    else:
        now_dt = datetime.now()
        for i in range(6, -1, -1):
            t_label = "Now" if i == 0 else f"-{i*5}m"
            threat_trend.append({"time": t_label, "legitimate": 0, "attacks": 0})

    # Recent Logs (actual records from Log table)
    recent_logs_objs = db.query(Log).order_by(desc(Log.timestamp)).limit(6).all()
    recent_logs = [
        {
            "id": l.id,
            "time": l.timestamp.strftime("%H:%M:%S") if l.timestamp else "Just now",
            "event": l.event_type,
            "details": l.details,
            "status": l.status
        }
        for l in recent_logs_objs
    ]

    # Live System Resources
    try:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
    except Exception:
        cpu = 15.0
        mem = 40.0

    recent_actions = db.query(Log).filter(Log.timestamp >= now_utc - timedelta(minutes=5)).count()
    sim_load = round(min(100.0, max(5.0, recent_actions * 12.5 + (cpu * 0.4))), 1)

    sys_resources = SystemResourceMetrics(
        cpu_usage_percent=round(cpu, 1),
        memory_usage_percent=round(mem, 1),
        simulation_load_percent=sim_load,
        simulator_status="Healthy (Qiskit Aer Ready)"
    )

    return DashboardSummaryResponse(
        total_signatures=total_sigs,
        signatures_trend_pct=signatures_trend_pct,
        verified_count=verified_legit,
        verified_success_rate=success_rate,
        detected_attacks=detected_attacks,
        detection_rate_pct=detection_rate,
        system_status="Healthy",
        latest_result=latest_result,
        measurement_distribution=meas_dist,
        threat_trend=threat_trend,
        recent_logs=recent_logs,
        system_resources=sys_resources
    )
