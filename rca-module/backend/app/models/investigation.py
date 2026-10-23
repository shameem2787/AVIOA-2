from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    deviation_id = Column(String(64), unique=True, index=True, nullable=True)
    title = Column(String(512), nullable=True)
    status = Column(String(64), default="Draft")  # Draft | Under Investigation | Ready for Review | Closed

    # 1. Incident Identification
    date_of_occurrence = Column(String(64), nullable=True)
    date_reported = Column(String(64), nullable=True)
    product_name = Column(String(256), nullable=True)
    batch_lot = Column(String(128), nullable=True)
    area_equipment = Column(String(256), nullable=True)
    process_step = Column(String(256), nullable=True)
    severity = Column(String(32), nullable=True)  # Critical | Major | Minor

    # 2. Incident Details
    description = Column(Text, nullable=True)
    immediate_actions = Column(Text, nullable=True)
    affected_quantity = Column(String(128), nullable=True)
    impact_summary = Column(Text, nullable=True)

    # 3. Investigation Approach
    investigation_method = Column(String(64), default="5 Whys + Fishbone")
    five_whys = Column(JSON, nullable=True)  # list of {why, answer}
    fishbone = Column(JSON, nullable=True)  # {man, machine, material, method, measurement, environment}

    # 4. Root Cause Analysis
    potential_root_causes = Column(JSON, nullable=True)  # list of {cause, evidence, confidence}
    contributing_factors = Column(JSON, nullable=True)
    missing_evidence = Column(JSON, nullable=True)  # list of strings
    evidence_notes = Column(Text, nullable=True)

    # 5. CAPA
    corrective_actions = Column(JSON, nullable=True)  # list of {action, owner, due_date, rationale}
    preventive_actions = Column(JSON, nullable=True)
    capa_summary = Column(Text, nullable=True)

    # Meta
    source_type = Column(String(32), nullable=True)  # text | pdf | email
    source_filename = Column(String(256), nullable=True)
    ai_risk_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_committed = Column(Boolean, default=False)
