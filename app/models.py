# Author: Sanidayal Gupta
import uuid
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Numeric, Boolean, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.database import Base

class ApartmentUnit(Base):
    __tablename__ = "apartment_units"

    id = Column(Integer, primary_key=True, index=True)
    unit_number = Column(String(20), unique=True, index=True, nullable=False)  # e.g., "502", "A-101"
    wing = Column(String(10), nullable=False)
    square_feet = Column(Integer, default=1200)
    monthly_maintenance_fee = Column(Numeric(10, 2), default=3500.00)

    residents = relationship("ResidentProfile", back_populates="unit")
    tickets = relationship("CommunityTicket", back_populates="unit")
    bills = relationship("MaintenanceBill", back_populates="unit")

class ResidentProfile(Base):
    __tablename__ = "resident_profiles"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("apartment_units.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    occupancy_type = Column(String(20), default="OWNER")  # OWNER, TENANT
    is_primary_contact = Column(Boolean, default=True)

    unit = relationship("ApartmentUnit", back_populates="residents")

class GatePass(Base):
    __tablename__ = "gate_passes"

    id = Column(Integer, primary_key=True, index=True)
    pass_code = Column(String(6), index=True, nullable=False)  # 6-digit OTP
    unit_id = Column(Integer, ForeignKey("apartment_units.id"), nullable=False)
    visitor_name = Column(String(100), nullable=False)
    visitor_phone = Column(String(20), nullable=False)
    purpose = Column(String(50), default="GUEST")  # GUEST, DELIVERY, CAB, SERVICE
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AmenityReservation(Base):
    __tablename__ = "amenity_reservations"

    id = Column(Integer, primary_key=True, index=True)
    amenity_name = Column(String(100), index=True, nullable=False)  # CLUBHOUSE, TENNIS_COURT, BANQUET
    unit_id = Column(Integer, ForeignKey("apartment_units.id"), nullable=False)
    booking_date = Column(Date, nullable=False)
    start_time_hour = Column(Integer, nullable=False)  # 24-hr format (e.g. 18 for 6 PM)
    end_time_hour = Column(Integer, nullable=False)
    booking_fee = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow)

class MaintenanceBill(Base):
    __tablename__ = "maintenance_bills"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("apartment_units.id"), nullable=False)
    billing_month = Column(Date, nullable=False)
    amount_due = Column(Numeric(10, 2), nullable=False)
    amount_paid = Column(Numeric(10, 2), default=0.00)
    is_settled = Column(Boolean, default=False)
    due_date = Column(Date, nullable=False)

    unit = relationship("ApartmentUnit", back_populates="bills")

class CommunityTicket(Base):
    __tablename__ = "community_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    unit_id = Column(Integer, ForeignKey("apartment_units.id"), nullable=False)
    category = Column(String(50), nullable=False)  # PLUMBING, ELECTRICAL, ELEVATOR, SECURITY
    priority = Column(String(20), default="NORMAL")  # LOW, NORMAL, HIGH, EMERGENCY
    description = Column(Text, nullable=False)
    assigned_vendor = Column(String(100), nullable=True)
    status = Column(String(50), default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)

    unit = relationship("ApartmentUnit", back_populates="tickets")
