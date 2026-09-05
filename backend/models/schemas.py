from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field
import hashlib


# ── Job ──────────────────────────────────────────────────────────────────────

class JobBase(SQLModel):
    title: str
    company: str
    url: str
    location: Optional[str] = None
    work_mode: Optional[str] = None          # Remote / Hybrid / On-site
    salary_min: Optional[float] = None       # in LPA
    salary_max: Optional[float] = None       # in LPA
    grad_year: Optional[str] = None          # e.g. "2025", "2025,2026"
    company_type: Optional[str] = None       # Product / MNC / Startup / Service
    relevance_score: Optional[float] = None  # 0-10, set by Filter Agent
    posted_date: Optional[str] = None
    raw_description: Optional[str] = None


class Job(JobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    seen_hash: str = Field(index=True)       # dedup key
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    emailed: bool = Field(default=False)

    @staticmethod
    def make_hash(title: str, company: str, url: str) -> str:
        raw = f"{title.lower().strip()}|{company.lower().strip()}|{url.strip()}"
        return hashlib.md5(raw.encode()).hexdigest()


class JobRead(JobBase):
    id: int
    seen_hash: str
    first_seen: datetime
    emailed: bool


# ── User Profile ──────────────────────────────────────────────────────────────

class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    grad_year: str = Field(default="2025")           # Hard filter
    preferred_roles: str = Field(default="SDE")      # comma-separated
    min_salary_lpa: float = Field(default=0.0)       # Soft filter
    preferred_locations: str = Field(default="")     # comma-separated
    preferred_work_mode: str = Field(default="")     # Remote/Hybrid/On-site
    preferred_company_types: str = Field(default="") # Product/MNC/Startup
    alert_email: str = Field(default="")
    relevance_threshold: float = Field(default=5.0)  # min score to include
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfileRead(SQLModel):
    id: int
    grad_year: str
    preferred_roles: str
    min_salary_lpa: float
    preferred_locations: str
    preferred_work_mode: str
    preferred_company_types: str
    alert_email: str
    relevance_threshold: float
    updated_at: datetime


class UserProfileUpdate(SQLModel):
    grad_year: Optional[str] = None
    preferred_roles: Optional[str] = None
    min_salary_lpa: Optional[float] = None
    preferred_locations: Optional[str] = None
    preferred_work_mode: Optional[str] = None
    preferred_company_types: Optional[str] = None
    alert_email: Optional[str] = None
    relevance_threshold: Optional[float] = None


# ── Run Log ───────────────────────────────────────────────────────────────────

class RunLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    status: str = Field(default="running")   # running / success / failed
    jobs_crawled: int = Field(default=0)
    jobs_after_filter: int = Field(default=0)
    jobs_new: int = Field(default=0)
    email_sent: bool = Field(default=False)
    error_message: Optional[str] = None


class RunLogRead(SQLModel):
    id: int
    started_at: datetime
    finished_at: Optional[datetime]
    status: str
    jobs_crawled: int
    jobs_after_filter: int
    jobs_new: int
    email_sent: bool
    error_message: Optional[str]
