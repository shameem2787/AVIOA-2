from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class WhyStep(BaseModel):
    why: str
    answer: str


class FishboneFactors(BaseModel):
    man: List[str] = []
    machine: List[str] = []
    material: List[str] = []
    method: List[str] = []
    measurement: List[str] = []
    environment: List[str] = []


class RootCauseItem(BaseModel):
    cause: str
    evidence: str = ""
    confidence: str = "Medium"  # High | Medium | Low


class CAPAItem(BaseModel):
    action: str
    owner: str = "QA Team"
    due_date: str = ""
    rationale: str = ""


class InvestigationBase(BaseModel):
    deviation_id: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = "Draft"
    date_of_occurrence: Optional[str] = None
    date_reported: Optional[str] = None
    product_name: Optional[str] = None
    batch_lot: Optional[str] = None
    area_equipment: Optional[str] = None
    process_step: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    immediate_actions: Optional[str] = None
    affected_quantity: Optional[str] = None
    impact_summary: Optional[str] = None
    investigation_method: Optional[str] = "5 Whys + Fishbone"
    five_whys: Optional[List[WhyStep]] = None
    fishbone: Optional[FishboneFactors] = None
    potential_root_causes: Optional[List[RootCauseItem]] = None
    contributing_factors: Optional[List[str]] = None
    missing_evidence: Optional[List[str]] = None
    evidence_notes: Optional[str] = None
    corrective_actions: Optional[List[CAPAItem]] = None
    preventive_actions: Optional[List[CAPAItem]] = None
    capa_summary: Optional[str] = None
    source_type: Optional[str] = None
    source_filename: Optional[str] = None
    ai_risk_notes: Optional[str] = None
    is_committed: Optional[bool] = False


class InvestigationCreate(InvestigationBase):
    pass


class InvestigationUpdate(InvestigationBase):
    pass


class InvestigationOut(InvestigationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    role: str  # user | assistant | system
    content: str


class ChatRequest(BaseModel):
    message: str
    investigation_id: Optional[int] = None
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str
    investigation: Optional[InvestigationOut] = None
    form_updates: Optional[Dict[str, Any]] = None
    tools_used: Optional[List[str]] = []


class UploadResponse(BaseModel):
    filename: str
    extracted_text: str
    investigation: Optional[InvestigationOut] = None
    reply: str
