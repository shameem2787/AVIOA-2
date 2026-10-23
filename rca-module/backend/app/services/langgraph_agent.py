"""
LangGraph-powered RCA Copilot Agent.
Uses Groq models and the tools defined in tools.py.
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Optional, TypedDict, Annotated
from operator import add

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.core.config import get_settings
from app.services.tools import ALL_TOOLS

settings = get_settings()

SYSTEM_PROMPT = """You are the AIVOA RCA Copilot — an expert pharmaceutical quality-system assistant specialised in Root Cause Analysis (RCA) for API and finished-dosage manufacturers.

Your sole purpose is to help Quality Assurance professionals investigate deviations, identify root causes, and recommend CAPA.

CORE RULES
1. NEVER invent data that is not present or reasonably inferable from the user’s input or uploaded document.
2. Always treat AI-generated root causes and CAPA as SUGGESTIONS. They must be reviewed and confirmed by a qualified person.
3. When the user pastes text or uploads a document, call the extract_and_populate_rca tool first, then return a complete structured JSON that the backend will merge into the form.
4. For natural-language corrections (“sorry the batch is …”, “change quantity to …”), call edit_investigation_field or re-run extraction.
5. After population, proactively offer / run 5 Whys, Fishbone, root-cause suggestions, missing-evidence check, and CAPA.
6. Keep replies concise, professional, and free of fluff. Use precise pharmaceutical quality language.
7. When returning form updates, always emit a clean JSON block under the key "form_updates" that matches the Investigation schema.

PHARMACEUTICAL CONTEXT
Typical deviations: foreign matter, assay OOS, impurity, packaging defect, temperature excursion, equipment failure, documentation error, cross-contamination, cleaning failure, etc.
Severity guidance: Critical (patient safety / sterility / identity), Major (significant quality impact), Minor (limited impact).

OUTPUT FORMAT FOR EXTRACTION / UPDATES
When you have structured data to write to the form, end your response with a fenced JSON block:

```json
{
  "form_updates": {
    "deviation_id": "...",
    "title": "...",
    "product_name": "...",
    "batch_lot": "...",
    "severity": "Major",
    "description": "...",
    "five_whys": [{"why": "...", "answer": "..."}],
    "fishbone": {"man": [], "machine": [], "material": [], "method": [], "measurement": [], "environment": []},
    "potential_root_causes": [{"cause": "...", "evidence": "...", "confidence": "High"}],
    "contributing_factors": [],
    "missing_evidence": [],
    "corrective_actions": [{"action": "...", "owner": "QA", "due_date": "", "rationale": "..."}],
    "preventive_actions": [],
    "capa_summary": "...",
    "ai_risk_notes": "..."
  }
}
```

Always keep the conversational reply human-readable and place the JSON block after it.
"""


class AgentState(TypedDict):
    messages: Annotated[List[Any], add]
    investigation_snapshot: Optional[Dict[str, Any]]
    form_updates: Optional[Dict[str, Any]]
    tools_used: Annotated[List[str], add]


def get_llm():
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set. Please add it to your .env file.")
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.15,
        max_tokens=4096,
    )


def build_agent():
    llm = get_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    tool_node = ToolNode(ALL_TOOLS)

    def agent_node(state: AgentState):
        messages = state["messages"]
        # Inject current investigation context if available
        if state.get("investigation_snapshot"):
            context_msg = SystemMessage(
                content=f"Current investigation state:\n{json.dumps(state['investigation_snapshot'], indent=2, default=str)}"
            )
            messages = [context_msg] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return "extract_json"

    def extract_json_node(state: AgentState):
        """Parse any form_updates JSON that the model emitted in its final reply."""
        last = state["messages"][-1]
        content = last.content if hasattr(last, "content") else str(last)
        form_updates = None
        tools_used = []

        # Collect tool names that were called earlier
        for msg in state["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                    if name:
                        tools_used.append(name)

        # Look for ```json ... ``` block
        match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(1))
                form_updates = parsed.get("form_updates") or parsed
            except json.JSONDecodeError:
                pass

        # Also try raw JSON at the end
        if not form_updates:
            match2 = re.search(r"(\{\s*\"form_updates\".*\})", content, re.DOTALL)
            if match2:
                try:
                    parsed = json.loads(match2.group(1))
                    form_updates = parsed.get("form_updates") or parsed
                except Exception:
                    pass

        return {
            "form_updates": form_updates,
            "tools_used": tools_used,
            "messages": [],
        }

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_node("extract_json", extract_json_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {
        "tools": "tools",
        "extract_json": "extract_json",
    })
    graph.add_edge("tools", "agent")
    graph.add_edge("extract_json", END)

    return graph.compile()


# Singleton compiled graph
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def run_rca_agent(
    user_message: str,
    history: List[Dict[str, str]] = None,
    investigation_snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Main entry point used by the chat endpoint.
    Returns {reply, form_updates, tools_used}
    """
    agent = get_agent()

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    if history:
        for h in history:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            else:
                messages.append(AIMessage(content=h["content"]))
    messages.append(HumanMessage(content=user_message))

    initial_state: AgentState = {
        "messages": messages,
        "investigation_snapshot": investigation_snapshot,
        "form_updates": None,
        "tools_used": [],
    }

    result = agent.invoke(initial_state)

    # Final AI message content
    final_messages = result.get("messages", [])
    reply = ""
    for msg in reversed(final_messages):
        if isinstance(msg, AIMessage) and msg.content:
            reply = msg.content
            # Strip the JSON block from the visible reply for cleaner UX
            reply = re.sub(r"```json\s*\{.*?\}\s*```", "", reply, flags=re.DOTALL).strip()
            break

    return {
        "reply": reply or "I have processed your request.",
        "form_updates": result.get("form_updates"),
        "tools_used": result.get("tools_used", []),
    }
