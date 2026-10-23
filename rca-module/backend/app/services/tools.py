"""
LangGraph / LangChain tools for the RCA Copilot.
These tools are the only way the AI is allowed to mutate the investigation form.
"""

from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import json


class ExtractIncidentInput(BaseModel):
    raw_text: str = Field(..., description="Full free-text complaint, email body, or PDF-extracted text")


class EditFieldInput(BaseModel):
    field_path: str = Field(..., description="Dot path e.g. product_name, five_whys.0.answer, corrective_actions.1.action")
    new_value: str = Field(..., description="New value for the field (stringified if complex)")


class RunFiveWhysInput(BaseModel):
    problem_statement: str = Field(..., description="Clear statement of the problem to investigate")


class RunFishboneInput(BaseModel):
    problem_statement: str = Field(..., description="Problem statement for fishbone analysis")


class SuggestRootCausesInput(BaseModel):
    context: str = Field(..., description="Current investigation context and evidence")


class SuggestCAPAInput(BaseModel):
    root_causes: str = Field(..., description="Identified or suspected root causes")
    severity: str = Field(default="Major", description="Severity level")


@tool("extract_and_populate_rca", args_schema=ExtractIncidentInput)
def extract_and_populate_rca(raw_text: str) -> str:
    """
    Primary intake tool. Parse free text / email / PDF content and return a structured
    JSON object that the system will merge into the RCA form. Always call this first
    when the user pastes a new incident description or uploads a document.
    """
    # The actual LLM reasoning happens in the agent; this tool is a signal + schema.
    return json.dumps({
        "status": "ready_for_llm_extraction",
        "instruction": "Extract all relevant fields into a complete InvestigationUpdate-compatible JSON."
    })


@tool("edit_investigation_field")
def edit_investigation_field(field_path: str, new_value: str) -> str:
    """
    Update a single field (or nested field) on the current investigation.
    Use for natural-language corrections such as 'change batch number to MFH260712A'
    or 'update affected quantity to 50 kg'.
    """
    return json.dumps({"field_path": field_path, "new_value": new_value, "status": "queued"})


@tool("run_5_whys", args_schema=RunFiveWhysInput)
def run_5_whys(problem_statement: str) -> str:
    """
    Perform a classic 5 Whys analysis on the given problem statement.
    Returns a list of {why, answer} pairs that will be written to the form.
    """
    return json.dumps({"problem": problem_statement, "status": "ready_for_llm_5whys"})


@tool("run_fishbone", args_schema=RunFishboneInput)
def run_fishbone(problem_statement: str) -> str:
    """
    Perform Ishikawa / Fishbone analysis across the six categories:
    Man, Machine, Material, Method, Measurement, Environment.
    """
    return json.dumps({"problem": problem_statement, "status": "ready_for_llm_fishbone"})


@tool("suggest_root_causes", args_schema=SuggestRootCausesInput)
def suggest_root_causes(context: str) -> str:
    """
    Based on the current investigation data and evidence, propose ranked potential
    root causes with supporting evidence and confidence levels.
    """
    return json.dumps({"context": context, "status": "ready_for_llm_root_causes"})


@tool("suggest_capa", args_schema=SuggestCAPAInput)
def suggest_capa(root_causes: str, severity: str = "Major") -> str:
    """
    Generate Corrective and Preventive Actions (CAPA) recommendations with owners,
    suggested due dates, and short rationales.
    """
    return json.dumps({
        "root_causes": root_causes,
        "severity": severity,
        "status": "ready_for_llm_capa"
    })


@tool("identify_missing_evidence")
def identify_missing_evidence(current_data: str) -> str:
    """
    Review the current investigation state and list specific pieces of evidence
    or information still needed before a root cause can be confirmed.
    """
    return json.dumps({"current_data": current_data, "status": "ready_for_llm_missing_evidence"})


ALL_TOOLS = [
    extract_and_populate_rca,
    edit_investigation_field,
    run_5_whys,
    run_fishbone,
    suggest_root_causes,
    suggest_capa,
    identify_missing_evidence,
]
