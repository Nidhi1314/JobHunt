from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from backend.db.database import get_session
from backend.models.schemas import (
    Job, JobRead,
    UserProfile, UserProfileRead, UserProfileUpdate,
    RunLog, RunLogRead
)
from datetime import datetime

router = APIRouter()


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health")
def health_check():
    return {"status": "ok", "message": "JobHunt AI is running 🚀"}


# ── Jobs ──────────────────────────────────────────────────────────────────────

@router.get("/jobs", response_model=List[JobRead])
def get_jobs(
    skip: int = 0,
    limit: int = 50,
    company: str = None,
    session: Session = Depends(get_session)
):
    query = select(Job).offset(skip).limit(limit).order_by(Job.first_seen.desc())
    if company:
        query = query.where(Job.company.ilike(f"%{company}%"))
    return session.exec(query).all()


@router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: int, session: Session = Depends(get_session)):
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get("/profile", response_model=UserProfileRead)
def get_profile(session: Session = Depends(get_session)):
    profile = session.exec(select(UserProfile)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/profile", response_model=UserProfileRead)
def update_profile(
    data: UserProfileUpdate,
    session: Session = Depends(get_session)
):
    profile = session.exec(select(UserProfile)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    profile.updated_at = datetime.utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


# ── Pipeline ──────────────────────────────────────────────────────────────────

@router.post("/pipeline/run")
def trigger_pipeline():
    # Stub — will wire to LangGraph in Phase 3
    return {"status": "triggered", "message": "Pipeline will be wired in Phase 3"}


@router.get("/pipeline/status", response_model=List[RunLogRead])
def get_pipeline_status(
    limit: int = 5,
    session: Session = Depends(get_session)
):
    logs = session.exec(
        select(RunLog).order_by(RunLog.started_at.desc()).limit(limit)
    ).all()
    return logs

@router.post("/pipeline/run-and-email")
async def trigger_pipeline_with_email():
    """Manually trigger full pipeline + send email."""
    from backend.graph.pipeline import run_pipeline
    from backend.email_sender.gmail_sender import send_job_alert_async

    result = await run_pipeline()
    new_jobs = result.get("new_jobs", [])
    email_sent = False

    if new_jobs:
        email_sent = await send_job_alert_async(new_jobs)

    return {
        "status": "complete",
        "jobs_crawled": result.get("jobs_crawled", 0),
        "jobs_new": result.get("jobs_new", 0),
        "email_sent": email_sent,
    }
