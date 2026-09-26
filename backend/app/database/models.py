from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.session import Base

def utc_now():
    return datetime.now(timezone.utc)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    signatures = relationship("Signature", back_populates="message", cascade="all, delete-orphan")

class Signature(Base):
    __tablename__ = "signatures"

    id = Column(Integer, primary_key=True, index=True)
    signature_id = Column(String(64), unique=True, index=True, nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    hash = Column(String(64), nullable=False, index=True)
    state_vector = Column(Text, nullable=False)  # JSON string of [complex/real components]
    theta = Column(Float, nullable=False)
    phi = Column(Float, nullable=False)
    circuit = Column(Text, nullable=False)  # QASM or circuit description
    measurement_counts = Column(Text, nullable=False)  # JSON string of {"0": c0, "1": c1}
    shots = Column(Integer, default=1024)
    fidelity = Column(Float, default=1.0)
    correction = Column(String(32), default="None")
    nonce = Column(String(64), nullable=True)
    is_used = Column(Boolean, default=False)
    status = Column(String(32), default="generated")
    timestamp = Column(DateTime, default=utc_now)

    message = relationship("Message", back_populates="signatures")
    verifications = relationship("Verification", back_populates="signature", cascade="all, delete-orphan")
    attacks = relationship("Attack", back_populates="signature", cascade="all, delete-orphan")

class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    signature_id = Column(String(64), ForeignKey("signatures.signature_id"), nullable=False, index=True)
    message_content = Column(Text, nullable=True)
    observed_counts = Column(Text, nullable=False)  # JSON string
    expected_distribution = Column(Text, nullable=False)  # JSON string {"0": p0, "1": p1}
    observed_distribution = Column(Text, nullable=False)  # JSON string {"0": p0, "1": p1}
    basis_distributions = Column(Text, nullable=True)  # JSON string for Z, X, Y bases
    fidelity = Column(Float, nullable=False)
    deviation = Column(Float, nullable=False)
    bit_error_rate = Column(Float, default=0.0)
    threat_score = Column(Float, default=0.0)
    decision = Column(String(32), nullable=False)  # "LEGITIMATE", "ATTACK DETECTED", "INVALID"
    verification_time_ms = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=utc_now)

    signature = relationship("Signature", back_populates="verifications")

class Attack(Base):
    __tablename__ = "attacks"

    id = Column(Integer, primary_key=True, index=True)
    signature_id = Column(String(64), ForeignKey("signatures.signature_id"), nullable=True, index=True)
    attack_type = Column(String(64), nullable=False)  # Forgery, Impersonation, Replay, Channel Manipulation, Unauthorized Verification
    parameters = Column(Text, nullable=False)  # JSON string of attack parameters
    modified_state = Column(Text, nullable=True)  # JSON string of altered state parameters
    expected_distribution = Column(Text, nullable=True)  # JSON
    observed_distribution = Column(Text, nullable=True)  # JSON
    fidelity = Column(Float, nullable=False)
    deviation = Column(Float, nullable=False)
    threat_score = Column(Float, nullable=False)
    decision = Column(String(64), nullable=False)
    attacker_info = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utc_now)

    signature = relationship("Signature", back_populates="attacks")

class QuantumCircuitRecord(Base):
    __tablename__ = "quantum_circuits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    qubits = Column(Integer, default=2)
    depth = Column(Integer, default=2)
    gates = Column(Integer, default=2)
    circuit_type = Column(String(64), default="Custom")
    qiskit_code = Column(Text, nullable=False)
    circuit_data = Column(Text, nullable=True)  # JSON grid or gate sequence
    created_at = Column(DateTime, default=utc_now)

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    event_type = Column(String(64), nullable=False)
    category = Column(String(64), nullable=False)  # "Signature", "Verification", "Attack", "Quantum", "Security", "System"
    details = Column(Text, nullable=False)
    status = Column(String(32), nullable=False)  # "Success", "Detected", "Blocked", "Warning", "Error", "Legitimate"
    source = Column(String(64), default="System")
    signature_id = Column(String(64), nullable=True)

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(64), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

# --- QDS Step 3 Database Models ---
class QDSNonce(Base):
    __tablename__ = "qds_nonces"

    id = Column(Integer, primary_key=True, index=True)
    nonce = Column(String(64), unique=True, index=True, nullable=False)
    key_id = Column(String(64), nullable=True, index=True)
    signature_id = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=False)
    is_consumed = Column(Boolean, default=False)
    consumed_at = Column(DateTime, nullable=True)

class QDSVerifier(Base):
    __tablename__ = "qds_verifiers"

    id = Column(Integer, primary_key=True, index=True)
    verifier_id = Column(String(64), unique=True, index=True, nullable=False)
    auth_token = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

class QDSClientRateLimit(Base):
    __tablename__ = "qds_rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(64), index=True, nullable=False)
    request_timestamp = Column(DateTime, default=utc_now, index=True)
    endpoint = Column(String(64), default="/api/qds/verify")

from app.database.session import engine
Base.metadata.create_all(bind=engine)


