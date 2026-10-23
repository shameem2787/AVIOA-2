# AIVOA · AI-Powered Root Cause Analysis (RCA) Module

Pharmaceutical Quality System — Deviation Investigation · 5 Whys · Fishbone · CAPA

---

## Overview

This is a complete, production-structured application built for the **AIVOA.AI AI Product Engineer Challenge**.

It implements an AI-assisted Root Cause Analysis workflow for API / FDF manufacturers:

- Paste text, email body, or upload a PDF
- AI extracts structured data and populates the RCA form
- Runs 5 Whys + Fishbone analysis
- Surfaces potential root causes, contributing factors, and missing evidence
- Recommends Corrective & Preventive Actions (CAPA)
- User reviews / edits via natural language; form updates automatically
- Investigation can be committed to the ledger

**Tech Stack (mandatory)**
- Frontend: React + Redux Toolkit + Vite
- Backend: Python + FastAPI
- AI: LangGraph + Groq (llama-3.3-70b-versatile / gemma2-9b-it)
- Database: SQLite (default) or PostgreSQL

**Design**
- Glassmorphism + Liquid morphism only
- Palette: Charcoal black · Soft gold · Silver · Warm white
- No blue / purple accents

---

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set your GROQ_API_KEY

uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 3. Groq API Key

Get a free key at https://console.groq.com/keys  
Paste it into `backend/.env`:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## Sample Inputs

Use the files in `sample_data/`:

1. `sample_deviation_email.txt` — Foreign matter in Metformin API
2. `sample_deviation_2.txt` — Assay OOS on Amoxicillin

Paste the content into the RCA Copilot or upload as a text/PDF file.

---

## Project Structure

```
rca-module/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/          # config, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── routers/       # FastAPI routes
│   │   └── services/      # LangGraph agent, tools, extraction
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/    # Layout, Form, Chat, UI
│   │   ├── store/         # Redux slices
│   │   ├── styles/        # Global + component CSS
│   │   └── utils/
│   ├── package.json
│   └── vite.config.js
├── sample_data/
└── README.md
```

---

## Key API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST   | /api/chat | Main AI interaction (text → form updates) |
| POST   | /api/upload | PDF / text upload + extraction |
| GET    | /api/investigations | List investigations |
| PATCH  | /api/investigations/{id} | Manual field updates |
| POST   | /api/investigations/{id}/commit | Commit investigation |

---

## AI Tools (LangGraph)

- `extract_and_populate_rca`
- `edit_investigation_field`
- `run_5_whys`
- `run_fishbone`
- `suggest_root_causes`
- `suggest_capa`
- `identify_missing_evidence`

---

## Notes for Demo Videos

1. **Product Demo** — Show paste → extraction → form fill → 5 Whys / Fishbone → CAPA → natural-language edit → commit.
2. **Code Walkthrough** — Cover Redux flow, FastAPI endpoints, LangGraph agent, tool calling, and DB persistence.

Do **not** push this repository to any public GitHub.

---

Built for the AIVOA AI Product Engineer Challenge · 2026
