# Smart Local Community & Apartment Society OS 🏢🤖

**Author:** Sanidayal Gupta  
**Contact:** sanidayalgupta10799@gmail.com | [LinkedIn](https://linkedin.com/in/sanidayalgupta)

---

A production-grade, pure backend autonomous digital management operating system for residential housing complexes, apartment societies, and gated communities. 

Built with **FastAPI**, **PostgreSQL (Asyncpg + SQLAlchemy 2.0)**, **Redis (Atomic Distributed Locks)**, the **Google GenAI SDK (`google-genai`)**, and standardized **Model Context Protocol (MCP)** tool contracts.

---

## 🛑 The Real-World Problem

Managing residential societies currently relies on chaotic WhatsApp groups, manual paper logbooks at security gates, and fragmented spreadsheets:
1. **Unstructured Complaints & Slow Dispatch:** Residents post vague complaints in community chats (*"Water dripping from the floor above, fix it!"*). Society managers take hours or days to manually triage urgency, find active plumbers or electricians, and follow up.
2. **Double-Booking & Hall Rental Conflicts:** Shared amenities (clubhouse, tennis court, community hall) are frequently double-booked when multiple residents request the same slot simultaneously.
3. **Visitor Gate Security Bottlenecks:** Delivery drivers and guests create gate congestion while guards make manual intercom phone calls to verify access.
4. **Maintenance Fee Tracking & Arrears:** Societies struggle to track partial payments, late payment interest, and enforce amenity restrictions on defaulters.

---

## 💡 The Solution: Autonomous Society Concierge Engine

This system replaces manual coordination with a high-concurrency API and an **Autonomous Agentic Workflow**:
* **Autonomous Complaint Triage & Dispatch:** Residents submit plain, conversational text. The Google GenAI SDK (Gemini) parses urgency, identifies the impacted flats, queries building records via MCP tools, and dispatches on-call vendors automatically.
* **Deterministic Mutex Amenity Booking:** Employs Redis-based distributed locking to guarantee zero double-booking on community amenities down to the millisecond.
* **Dynamic Gatekeeper OTP System:** Residents issue time-decaying 6-digit visitor passes verified instantly at guard terminals.
* **Relational Financial Ledger:** Maintains an audit trail for flat maintenance dues, payments, and late-fee calculations.

---

## 🏗️ Architectural Topology

```
 [ Gate Guard Terminal / Resident App / Webhooks ]
                        │
                        ▼
             [ FastAPI Ingestion API ]
                        │
      ┌─────────────────┴─────────────────┐
      ▼                                   ▼
 [ Direct Core Services ]       [ Autonomous Concierge Agent ]
 * Resident Directory           (Google GenAI SDK — Gemini 2.5)
 * Visitor Pass OTP Engine                │
 * Maintenance Dues Ledger                ▼
      │                        [ MCP Host Tool Router ]
      │                                   │
      │        ┌──────────────────────────┼──────────────────────────┐
      │        ▼                          ▼                          ▼
      │ [ check_resident_dues ] [ reserve_amenity_slot ] [ dispatch_vendor ]
      │        │                          │                          │
      └────────┴──────────────────────────┴──────────────────────────┘
                                          ▼
                      [ PostgreSQL 16 (Relational Engine) ]
```

---

## 🛠️ Tech Stack & Protocols

* **Backend Engine:** Python 3.11+, FastAPI (ASGI async architecture)
* **AI & Agentic Framework:** Google GenAI SDK (`google-genai`), Model Context Protocol (MCP) standardized tool calling
* **Relational Database:** PostgreSQL 16 with `asyncpg` and SQLAlchemy 2.0
* **Concurrency & Cache:** Redis (distributed locks, rate-limiting, and OTP caching)
* **Validation & Settings:** Pydantic v2 & Pydantic Settings

---

## 📂 Project Structure

```
smart-society-os/
├── app/
│   ├── __init__.py
│   ├── config.py             # Environment configurations
│   ├── database.py           # PostgreSQL Async session & engine
│   ├── models.py             # SQLAlchemy 2.0 ORM schemas
│   ├── schemas.py            # Pydantic v2 input/output validation
│   ├── mcp_tools.py          # Model Context Protocol standardized registry
│   ├── agent.py              # Google GenAI autonomous orchestration loop
│   └── main.py               # REST API endpoints & route handlers
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Setup & Execution Guide

### 1. Clone & Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
Update `.env` with your Google Gemini API key (`GEMINI_API_KEY`) and your local PostgreSQL and Redis connection URLs.

### 3. Run the Service
```bash
uvicorn app.main:app --reload --port 8000
```

Access the interactive OpenAPI Swagger documentation at: `http://127.0.0.1:8000/docs`

---

## 📋 End-to-End Practical Example

### Autonomous Resident Complaint Triage & Dispatch
Send a POST request to `/api/v1/agent/concierge`:

**Request Payload:**
```json
{
  "resident_id": 1,
  "flat_number": "502",
  "message": "Water is leaking heavily through the kitchen ceiling into my flat 502, looks like it's coming from flat 602 above. Need an emergency plumber right now!"
}
```

**Agent Execution Steps:**
1. Google GenAI extracts intent: Category = `PLUMBING`, Urgency = `EMERGENCY`, Origin Unit = `602`.
2. Agent automatically queries MCP tool `dispatch_maintenance_vendor` with category `PLUMBING`.
3. Agent commits an emergency `CommunityTicket` linked to unit `502` and `602`.
4. Returns an immediate structured response with the assigned vendor dispatch details and SLA resolution window.
