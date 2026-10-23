from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.database import get_db
from app.models.investigation import Investigation
from app.schemas.investigation import (
    InvestigationOut, InvestigationCreate, InvestigationUpdate,
    ChatRequest, ChatResponse, UploadResponse
)
from app.services.langgraph_agent import run_rca_agent
from app.services.extraction import extract_text_from_upload

router = APIRouter(prefix="/api", tags=["investigations"])


def _model_to_dict(inv: Investigation) -> dict:
    return {
        "id": inv.id,
        "deviation_id": inv.deviation_id,
        "title": inv.title,
        "status": inv.status,
        "date_of_occurrence": inv.date_of_occurrence,
        "date_reported": inv.date_reported,
        "product_name": inv.product_name,
        "batch_lot": inv.batch_lot,
        "area_equipment": inv.area_equipment,
        "process_step": inv.process_step,
        "severity": inv.severity,
        "description": inv.description,
        "immediate_actions": inv.immediate_actions,
        "affected_quantity": inv.affected_quantity,
        "impact_summary": inv.impact_summary,
        "investigation_method": inv.investigation_method,
        "five_whys": inv.five_whys,
        "fishbone": inv.fishbone,
        "potential_root_causes": inv.potential_root_causes,
        "contributing_factors": inv.contributing_factors,
        "missing_evidence": inv.missing_evidence,
        "evidence_notes": inv.evidence_notes,
        "corrective_actions": inv.corrective_actions,
        "preventive_actions": inv.preventive_actions,
        "capa_summary": inv.capa_summary,
        "source_type": inv.source_type,
        "source_filename": inv.source_filename,
        "ai_risk_notes": inv.ai_risk_notes,
        "is_committed": inv.is_committed,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
    }


def _apply_updates(inv: Investigation, updates: dict):
    """Safely apply a dict of form_updates onto the SQLAlchemy model."""
    simple_fields = [
        "deviation_id", "title", "status", "date_of_occurrence", "date_reported",
        "product_name", "batch_lot", "area_equipment", "process_step", "severity",
        "description", "immediate_actions", "affected_quantity", "impact_summary",
        "investigation_method", "evidence_notes", "capa_summary", "ai_risk_notes",
        "source_type", "source_filename", "is_committed"
    ]
    for f in simple_fields:
        if f in updates and updates[f] is not None:
            setattr(inv, f, updates[f])

    json_fields = [
        "five_whys", "fishbone", "potential_root_causes",
        "contributing_factors", "missing_evidence",
        "corrective_actions", "preventive_actions"
    ]
    for f in json_fields:
        if f in updates and updates[f] is not None:
            setattr(inv, f, updates[f])


@router.get("/investigations", response_model=List[InvestigationOut])
def list_investigations(db: Session = Depends(get_db)):
    items = db.query(Investigation).order_by(Investigation.id.desc()).limit(50).all()
    return items


@router.get("/investigations/{investigation_id}", response_model=InvestigationOut)
def get_investigation(investigation_id: int, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv


@router.post("/investigations", response_model=InvestigationOut)
def create_investigation(payload: InvestigationCreate, db: Session = Depends(get_db)):
    inv = Investigation(**payload.model_dump(exclude_unset=True))
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


@router.patch("/investigations/{investigation_id}", response_model=InvestigationOut)
def update_investigation(
    investigation_id: int,
    payload: InvestigationUpdate,
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    data = payload.model_dump(exclude_unset=True)
    _apply_updates(inv, data)
    db.commit()
    db.refresh(inv)
    return inv


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    inv = None
    snapshot = None
    if request.investigation_id:
        inv = db.query(Investigation).filter(Investigation.id == request.investigation_id).first()
        if inv:
            snapshot = _model_to_dict(inv)

    history = [{"role": h.role, "content": h.content} for h in (request.history or [])]

    try:
        result = run_rca_agent(
            user_message=request.message,
            history=history,
            investigation_snapshot=snapshot,
        )
    except ValueError as e:
        # Missing API key or similar
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    form_updates = result.get("form_updates")
    if form_updates and inv:
        _apply_updates(inv, form_updates)
        if not inv.status or inv.status == "Draft":
            inv.status = "Under Investigation"
        db.commit()
        db.refresh(inv)
    elif form_updates and not inv:
        # Create a new investigation from the extraction
        inv = Investigation()
        _apply_updates(inv, form_updates)
        inv.status = "Under Investigation"
        inv.source_type = inv.source_type or "text"
        db.add(inv)
        db.commit()
        db.refresh(inv)

    return ChatResponse(
        reply=result["reply"],
        investigation=inv,
        form_updates=form_updates,
        tools_used=result.get("tools_used", []),
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    investigation_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    content = await file.read()
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 15 MB)")

    extracted = extract_text_from_upload(file.filename or "document", content)
    if not extracted or extracted.startswith("[PDF extraction error"):
        # Still allow the AI to try with whatever we got
        pass

    inv = None
    if investigation_id:
        inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()

    prompt = (
        f"A pharmaceutical quality document named '{file.filename}' was uploaded. "
        f"Extract all relevant deviation / investigation data and populate the RCA form.\n\n"
        f"--- DOCUMENT CONTENT ---\n{extracted[:12000]}\n--- END ---"
    )

    snapshot = _model_to_dict(inv) if inv else None
    try:
        result = run_rca_agent(user_message=prompt, investigation_snapshot=snapshot)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    form_updates = result.get("form_updates") or {}
    form_updates["source_type"] = "pdf"
    form_updates["source_filename"] = file.filename

    if inv:
        _apply_updates(inv, form_updates)
        inv.status = inv.status or "Under Investigation"
        db.commit()
        db.refresh(inv)
    else:
        inv = Investigation()
        _apply_updates(inv, form_updates)
        inv.status = "Under Investigation"
        db.add(inv)
        db.commit()
        db.refresh(inv)

    return UploadResponse(
        filename=file.filename or "document",
        extracted_text=extracted[:2000] + ("..." if len(extracted) > 2000 else ""),
        investigation=inv,
        reply=result["reply"],
    )


@router.post("/investigations/{investigation_id}/commit", response_model=InvestigationOut)
def commit_investigation(investigation_id: int, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    inv.is_committed = True
    inv.status = "Ready for Review"
    db.commit()
    db.refresh(inv)
    return inv
