# Author: Sanidayal Gupta
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

class UnitCreate(BaseModel):
    unit_number: str = Field(..., example="502")
    wing: str = Field(..., example="A")
    square_feet: int = Field(1200, example=1200)
    monthly_maintenance_fee: Decimal = Field(3500.00, example=3500.00)

class UnitResponse(UnitCreate):
    id: int
    class Config:
        from_attributes = True

class ResidentCreate(BaseModel):
    unit_id: int
    first_name: str = Field(..., example="Sanidayal")
    last_name: str = Field(..., example="Gupta")
    email: str = Field(..., example="sanidayalgupta10799@gmail.com")
    phone_number: str = Field(..., example="+919876543210")
    occupancy_type: str = Field("OWNER", example="OWNER")

class ResidentResponse(ResidentCreate):
    id: int
    class Config:
        from_attributes = True

class GatePassGenerateRequest(BaseModel):
    unit_id: int
    visitor_name: str = Field(..., example="John Doe")
    visitor_phone: str = Field(..., example="+919811122233")
    purpose: str = Field("GUEST", example="DELIVERY")
    valid_hours: int = Field(4, example=4)

class GatePassResponse(BaseModel):
    pass_code: str
    visitor_name: str
    unit_id: int
    expires_at: datetime
    is_used: bool

    class Config:
        from_attributes = True

class GatePassVerifyRequest(BaseModel):
    pass_code: str = Field(..., example="582914")

class AmenityBookRequest(BaseModel):
    unit_id: int
    amenity_name: str = Field(..., example="CLUBHOUSE")
    booking_date: date = Field(..., example="2026-09-10")
    start_time_hour: int = Field(..., example=18)
    end_time_hour: int = Field(..., example=20)

class ConciergeChatRequest(BaseModel):
    resident_id: int = Field(..., example=1)
    flat_number: str = Field(..., example="502")
    message: str = Field(..., example="Water is leaking heavily through the kitchen ceiling into my flat 502, looks like it's coming from flat 602 above. Need an emergency plumber right now!")

class ConciergeChatResponse(BaseModel):
    triage_assessment: str
    assigned_category: str
    priority_level: str
    dispatched_vendor: Optional[str]
    ticket_id: Optional[str]
    agent_message_to_resident: str
