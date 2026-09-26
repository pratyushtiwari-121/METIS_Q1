from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.database.models import QuantumCircuitRecord, Log
from app.schemas.schemas import (
    CustomCircuitRequest,
    PredefinedCircuitRunRequest,
    CircuitRunResponse
)
from app.quantum.circuit_builder import run_predefined_circuit, run_custom_circuit
from app.quantum.teleportation import run_teleportation_protocol
from app.quantum.qber import compute_qber

router = APIRouter(prefix="/quantum", tags=["Quantum Circuit"])

@router.post("/circuit/predefined", response_model=CircuitRunResponse)
def execute_predefined_circuit(req: PredefinedCircuitRunRequest, db: Session = Depends(get_db)):
    c_name = req.circuit_name.lower()
    
    if c_name == "teleportation":
        theta_val = req.custom_state_angle if req.custom_state_angle is not None else 1.0472
        res = run_teleportation_protocol(theta=theta_val, phi=0.7854, shots=req.shots)
    else:
        res = run_predefined_circuit(c_name, shots=req.shots)

    # Log circuit execution
    db.add(Log(
        event_type="Quantum Simulation",
        category="Quantum",
        details=f"Executed predefined circuit '{res.name}' ({res.qubits} qubits, {req.shots} shots)",
        status="Success",
        source="Qiskit Aer Simulator"
    ))
    db.commit()

    return res

@router.post("/circuit/run", response_model=CircuitRunResponse)
def execute_custom_circuit(req: CustomCircuitRequest, db: Session = Depends(get_db)):
    if req.qubits < 1 or req.qubits > 5:
        raise HTTPException(status_code=400, detail="Qubit count must be between 1 and 5 for local simulator performance.")

    res = run_custom_circuit(
        qubits=req.qubits,
        gates=req.gates,
        shots=req.shots,
        circuit_name=req.name
    )

    db.add(Log(
        event_type="Quantum Simulation",
        category="Quantum",
        details=f"Executed custom circuit '{req.name}' ({req.qubits} qubits, {len(req.gates)} gates, {req.shots} shots)",
        status="Success",
        source="Circuit Builder"
    ))
    db.commit()

    return res

@router.post("/circuits")
def save_circuit(req: CustomCircuitRequest, db: Session = Depends(get_db)):
    rec = QuantumCircuitRecord(
        name=req.name,
        description=req.description,
        qubits=req.qubits,
        depth=len(req.gates),
        gates=len(req.gates),
        circuit_type="Custom",
        qiskit_code="# Custom Circuit",
        circuit_data=req.model_dump_json()
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"id": rec.id, "name": rec.name, "message": "Circuit saved successfully."}

@router.get("/circuits")
def list_circuits(db: Session = Depends(get_db)):
    circuits = db.query(QuantumCircuitRecord).order_by(desc(QuantumCircuitRecord.created_at)).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "qubits": c.qubits,
            "depth": c.depth,
            "gates": c.gates,
            "circuit_type": c.circuit_type,
            "created_at": c.created_at.isoformat() if c.created_at else ""
        }
        for c in circuits
    ]
    
@router.get("/qber", response_model=dict)
def get_qber(shots: int = 1024):
    """Return measurement-based QBER for X, Y, Z bases."""
    qber_stats = compute_qber(shots=shots)
    return qber_stats
