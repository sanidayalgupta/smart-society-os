# Author: Sanidayal Gupta
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.config import settings
from app.database import engine, Base, get_db
from app.models import ApartmentUnit, ResidentProfile, GatePass, AmenityReservation, CommunityTicket
from app.schemas import (
    UnitCreate, UnitResponse,
    ResidentCreate, ResidentResponse,
    GatePassGenerateRequest, GatePassResponse, GatePassVerifyRequest,
    AmenityBookRequest, ConciergeChatRequest, ConciergeChatResponse
)
from app.agent import run_society_concierge

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=f"Engineered by {settings.AUTHOR}. Pure Backend OS for Residential Housing Complexes."
)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "author": settings.AUTHOR,
        "engine": "FastAPI + Google GenAI SDK + PostgreSQL"
    }

# --- UNIT & RESIDENT DIRECTORY ---
@app.post("/api/v1/units", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(payload: UnitCreate, db: AsyncSession = Depends(get_db)):
    unit = ApartmentUnit(**payload.model_dump())
    db.add(unit)
    await db.commit()
    await db.refresh(unit)
    return unit

@app.post("/api/v1/residents", response_model=ResidentResponse, status_code=status.HTTP_201_CREATED)
async def register_resident(payload: ResidentCreate, db: AsyncSession = Depends(get_db)):
    resident = ResidentProfile(**payload.model_dump())
    db.add(resident)
    await db.commit()
    await db.refresh(resident)
    return resident

# --- VISITOR GATE PASS (OTP ENGINE) ---
@app.post("/api/v1/gate/passes/generate", response_model=GatePassResponse, status_code=status.HTTP_201_CREATED)
async def generate_visitor_pass(payload: GatePassGenerateRequest, db: AsyncSession = Depends(get_db)):
    # 6-digit random gate code
    otp_code = f"{random.randint(100000, 999999)}"
    expiry = datetime.utcnow() + timedelta(hours=payload.valid_hours)

    gate_pass = GatePass(
        pass_code=otp_code,
        unit_id=payload.unit_id,
        visitor_name=payload.visitor_name,
        visitor_phone=payload.visitor_phone,
        purpose=payload.purpose,
        expires_at=expiry
    )
    db.add(gate_pass)
    await db.commit()
    await db.refresh(gate_pass)
    return gate_pass

@app.post("/api/v1/gate/passes/verify")
async def verify_visitor_pass(payload: GatePassVerifyRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GatePass).where(GatePass.pass_code == payload.pass_code))
    gate_pass = result.scalar_one_or_none()

    if not gate_pass:
        raise HTTPException(status_code=404, detail="Invalid Gate Pass Code.")
    if gate_pass.is_used:
        raise HTTPException(status_code=400, detail="Gate Pass has already been used.")
    if gate_pass.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Gate Pass has expired.")

    gate_pass.is_used = True
    await db.commit()

    return {
        "status": "ACCESS_GRANTED",
        "visitor_name": gate_pass.visitor_name,
        "destination_unit_id": gate_pass.unit_id,
        "purpose": gate_pass.purpose
    }

# --- ATOMIC AMENITY RESERVATION ---
@app.post("/api/v1/amenities/reserve", status_code=status.HTTP_201_CREATED)
async def reserve_amenity(payload: AmenityBookRequest, db: AsyncSession = Depends(get_db)):
    # Check for slot conflicts
    existing_query = await db.execute(
        select(AmenityReservation).where(
            AmenityReservation.amenity_name == payload.amenity_name,
            AmenityReservation.booking_date == payload.booking_date,
            AmenityReservation.start_time_hour < payload.end_time_hour,
            AmenityReservation.end_time_hour > payload.start_time_hour
        )
    )
    conflict = existing_query.scalar_one_or_none()
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Amenity slot conflict. This facility is already booked during this time window."
        )

    reservation = AmenityReservation(**payload.model_dump())
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)

    return {
        "status": "RESERVATION_CONFIRMED",
        "reservation_id": reservation.id,
        "amenity": reservation.amenity_name,
        "date": reservation.booking_date
    }

# --- AUTONOMOUS SOCIETY CONCIERGE (GOOGLE GENAI + MCP AGENT) ---
@app.post("/api/v1/agent/concierge", response_model=ConciergeChatResponse)
async def society_concierge_endpoint(
    payload: ConciergeChatRequest,
    db: AsyncSession = Depends(get_db)
):
    # Execute the agentic loop
    agent_output = await run_society_concierge(
        resident_id=payload.resident_id,
        flat_number=payload.flat_number,
        raw_complaint=payload.message
    )

    # Persist the resulting ticket in PostgreSQL
    # Find unit by flat number
    unit_res = await db.execute(select(ApartmentUnit).where(ApartmentUnit.unit_number == payload.flat_number))
    unit = unit_res.scalar_one_or_none()
    unit_id = unit.id if unit else 1

    ticket = CommunityTicket(
        unit_id=unit_id,
        category=agent_output.get("assigned_category", "GENERAL"),
        priority=agent_output.get("priority_level", "NORMAL"),
        description=payload.message,
        assigned_vendor=agent_output.get("dispatched_vendor")
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    return ConciergeChatResponse(
        triage_assessment=agent_output.get("triage_assessment", "Triage complete."),
        assigned_category=agent_output.get("assigned_category", "GENERAL"),
        priority_level=agent_output.get("priority_level", "NORMAL"),
        dispatched_vendor=agent_output.get("dispatched_vendor"),
        ticket_id=ticket.ticket_uuid,
        agent_message_to_resident=agent_output.get("resident_message", "")
    )
