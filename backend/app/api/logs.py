import io
import csv
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.database.models import Log
from app.schemas.schemas import LogListResponse, LogItemResponse, LogSummaryStats

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("", response_model=LogListResponse)
def get_logs(
    category: str | None = None,
    status: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Log)

    if category and category.lower() != "all":
        query = query.filter(Log.category.ilike(f"%{category}%"))

    if status and status.lower() != "all":
        query = query.filter(Log.status.ilike(f"%{status}%"))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Log.details.ilike(search_pattern)) |
            (Log.event_type.ilike(search_pattern)) |
            (Log.source.ilike(search_pattern)) |
            (Log.signature_id.ilike(search_pattern))
        )

    total_count = query.count()
    logs_objs = query.order_by(desc(Log.timestamp)).offset((page - 1) * page_size).limit(page_size).all()

    # Calculate summary statistics across all logs
    all_logs = db.query(Log).all()
    total_logs = len(all_logs)
    success_count = sum(1 for l in all_logs if l.status in ("Success", "Legitimate"))
    detected_count = sum(1 for l in all_logs if "detected" in l.status.lower() or "attack" in l.event_type.lower())
    blocked_count = sum(1 for l in all_logs if "blocked" in l.status.lower())
    system_count = sum(1 for l in all_logs if l.category in ("System", "Quantum"))
    unauth_count = sum(1 for l in all_logs if "unauthorized" in l.details.lower() or "replay" in l.details.lower())

    cat_counts = {}
    for l in all_logs:
        cat_counts[l.category] = cat_counts.get(l.category, 0) + 1

    summary = LogSummaryStats(
        total_logs=total_logs,
        successful_events=success_count,
        detected_attacks=detected_count,
        blocked_attempts=blocked_count,
        system_events=system_count,
        unauthorized_access=unauth_count,
        events_by_category=cat_counts if cat_counts else {"Signature": 0, "Verification": 0, "Attack": 0, "Quantum": 0}
    )

    items = [
        LogItemResponse(
            id=l.id,
            timestamp=l.timestamp.strftime("%Y-%m-%d %H:%M:%S") if l.timestamp else "",
            event_type=l.event_type,
            category=l.category,
            details=l.details,
            status=l.status,
            source=l.source or "System",
            signature_id=l.signature_id
        )
        for l in logs_objs
    ]

    return LogListResponse(
        logs=items,
        summary=summary,
        page=page,
        page_size=page_size,
        total_count=total_count
    )

@router.get("/export")
def export_logs_csv(db: Session = Depends(get_db)):
    logs = db.query(Log).order_by(desc(Log.timestamp)).all()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Log ID", "Timestamp", "Event Type", "Category", "Details", "Status", "Source", "Signature ID"])
    for l in logs:
        writer.writerow([
            l.id,
            l.timestamp.isoformat() if l.timestamp else "",
            l.event_type,
            l.category,
            l.details,
            l.status,
            l.source,
            l.signature_id or ""
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=quantum_security_logs.csv"}
    )

@router.get("/{log_id}", response_model=LogItemResponse)
def get_log(log_id: int, db: Session = Depends(get_db)):
    l = db.query(Log).filter(Log.id == log_id).first()
    if not l:
        raise HTTPException(status_code=404, detail=f"Log {log_id} not found.")

    return LogItemResponse(
        id=l.id,
        timestamp=l.timestamp.strftime("%Y-%m-%d %H:%M:%S") if l.timestamp else "",
        event_type=l.event_type,
        category=l.category,
        details=l.details,
        status=l.status,
        source=l.source or "System",
        signature_id=l.signature_id
    )
