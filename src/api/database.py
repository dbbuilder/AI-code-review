"""
Database models and connection management for AutoRev API
"""

from datetime import datetime
from typing import Optional
import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# Database URL from environment (Railway provides DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL")

# SQLAlchemy setup
Base = declarative_base()
engine = None
SessionLocal = None


class AnalysisJob(Base):
    """
    Persistent storage for analysis jobs

    Replaces in-memory analysis_jobs dictionary
    """
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)  # queued, running, completed, failed
    repo_url = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    preset = Column(String, nullable=False)
    ai_provider = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    progress = Column(Integer, default=0)
    message = Column(Text, nullable=True)
    result_url = Column(String, nullable=True)
    error = Column(Text, nullable=True)

    # Store findings as JSON for completed analyses
    findings = Column(JSON, nullable=True)
    summary = Column(JSON, nullable=True)


class InvitationRequest(Base):
    """
    Invitation requests from users wanting access to AutoRev
    """
    __tablename__ = "invitation_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    company = Column(String, nullable=True)

    status = Column(String, nullable=False, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)  # Email of admin who reviewed

    # Clerk invitation
    clerk_invitation_id = Column(String, nullable=True)
    invited_at = Column(DateTime, nullable=True)


def init_db():
    """
    Initialize database connection

    Called on startup to create engine and session factory
    """
    global engine, SessionLocal

    try:
        if not DATABASE_URL:
            # Fallback to SQLite for local development
            print("WARNING: No DATABASE_URL found, using SQLite database")
            db_url = "sqlite:///./autorev.db"
        else:
            # Railway provides postgres:// but SQLAlchemy 2.0 requires postgresql://
            db_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
            print(f"Connecting to PostgreSQL database...")

        engine = create_engine(
            db_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,
            max_overflow=10
        )

        # Create tables if they don't exist
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        print(f"✅ Database initialized successfully: {db_url.split('@')[0]}@***")
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        print(f"DATABASE_URL present: {bool(DATABASE_URL)}")
        # Re-raise to prevent app from starting with broken database
        raise


@contextmanager
def get_db():
    """
    Context manager for database sessions

    Usage:
        with get_db() as db:
            job = db.query(AnalysisJob).filter_by(id=job_id).first()
    """
    if SessionLocal is None:
        init_db()

    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_job(job_id: str) -> Optional[AnalysisJob]:
    """Get analysis job by ID"""
    with get_db() as db:
        job = db.query(AnalysisJob).filter_by(id=job_id).first()
        if job:
            db.expunge(job)  # Detach from session so it can be used after
        return job


def create_job(job_data: dict) -> AnalysisJob:
    """Create new analysis job"""
    try:
        with get_db() as db:
            job = AnalysisJob(**job_data)
            db.add(job)
            db.commit()
            db.refresh(job)
            # Expunge from session so it can be used after session closes
            db.expunge(job)
            return job
    except Exception as e:
        print(f"❌ Failed to create job: {str(e)}")
        print(f"Job data: {job_data}")
        raise


def update_job(job_id: str, updates: dict) -> Optional[AnalysisJob]:
    """Update analysis job"""
    with get_db() as db:
        job = db.query(AnalysisJob).filter_by(id=job_id).first()
        if job:
            for key, value in updates.items():
                setattr(job, key, value)
            db.commit()
            db.refresh(job)
            db.expunge(job)  # Detach from session
        return job


def save_job_results(job_id: str, findings: list, summary: dict):
    """Save analysis results to database"""
    with get_db() as db:
        job = db.query(AnalysisJob).filter_by(id=job_id).first()
        if job:
            job.findings = findings
            job.summary = summary
            db.commit()


# Invitation Request Functions

def create_invitation_request(email: str, name: Optional[str] = None,
                              reason: Optional[str] = None, company: Optional[str] = None) -> InvitationRequest:
    """Create new invitation request"""
    try:
        with get_db() as db:
            invitation = InvitationRequest(
                email=email,
                name=name,
                reason=reason,
                company=company,
                status="pending",
                created_at=datetime.utcnow()
            )
            db.add(invitation)
            db.commit()
            db.refresh(invitation)
            db.expunge(invitation)
            return invitation
    except Exception as e:
        print(f"❌ Failed to create invitation request: {str(e)}")
        raise


def get_invitation_request_by_email(email: str) -> Optional[InvitationRequest]:
    """Get invitation request by email"""
    with get_db() as db:
        request = db.query(InvitationRequest).filter_by(email=email).first()
        if request:
            db.expunge(request)
        return request


def get_all_invitation_requests() -> list:
    """Get all invitation requests"""
    with get_db() as db:
        requests = db.query(InvitationRequest).order_by(InvitationRequest.created_at.desc()).all()
        # Expunge all from session
        for req in requests:
            db.expunge(req)
        return requests


def update_invitation_request(request_id: int, updates: dict) -> Optional[InvitationRequest]:
    """Update invitation request"""
    with get_db() as db:
        request = db.query(InvitationRequest).filter_by(id=request_id).first()
        if request:
            for key, value in updates.items():
                setattr(request, key, value)
            db.commit()
            db.refresh(request)
            db.expunge(request)
        return request
