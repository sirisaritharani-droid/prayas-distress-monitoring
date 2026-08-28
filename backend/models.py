import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    anonymous_case_id = Column(String(32), unique=True, index=True)
    email = Column(String(128), unique=True, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(32), default="survivor")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    consents = relationship("Consent", back_populates="user", cascade="all, delete-orphan")
    checkins = relationship("CheckIn", back_populates="user", cascade="all, delete-orphan")
    baseline = relationship("PersonalBaseline", back_populates="user", uselist=False, cascade="all, delete-orphan")
    followups = relationship("FollowUp", back_populates="user", cascade="all, delete-orphan")

class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    consent_version = Column(String(16), default="v1.0")
    accepted = Column(Boolean, default=False)
    share_optional_signals = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="consents")

class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    mood = Column(Float, nullable=False)
    stress = Column(Float, nullable=False)
    anxiety = Column(Float, nullable=False)
    sleep_hours = Column(Float, nullable=False)
    social_connection = Column(Float, nullable=False)
    safety = Column(Float, nullable=False)
    energy = Column(Float, nullable=False)
    optional_text = Column(Text, nullable=True)

    user = relationship("User", back_populates="checkins")

class PersonalBaseline(Base):
    __tablename__ = "baselines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    mood_baseline = Column(Float, default=7.0)
    stress_baseline = Column(Float, default=3.0)
    anxiety_baseline = Column(Float, default=3.0)
    sleep_baseline = Column(Float, default=7.0)
    social_baseline = Column(Float, default=7.0)
    safety_baseline = Column(Float, default=7.0)
    energy_baseline = Column(Float, default=7.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="baseline")

class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    counsellor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(32), default="NOT_REVIEWED")
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="followups")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, nullable=True)
    action = Column(String(128), nullable=False)
    details = Column(String(512), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
