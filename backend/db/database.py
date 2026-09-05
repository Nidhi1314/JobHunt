from sqlmodel import SQLModel, create_engine, Session, select
from backend.config import get_settings
from backend.models.schemas import Job, UserProfile, RunLog

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    connect_args={"check_same_thread": False},  # needed for SQLite
)


def create_db_and_tables():
    """Create all tables on startup."""
    SQLModel.metadata.create_all(engine)
    _seed_default_profile()


def get_session():
    """FastAPI dependency — yields a DB session."""
    with Session(engine) as session:
        yield session


def _seed_default_profile():
    """Insert a default user profile if none exists."""
    with Session(engine) as session:
        existing = session.exec(select(UserProfile)).first()
        if not existing:
            profile = UserProfile()
            session.add(profile)
            session.commit()


def job_exists(session: Session, seen_hash: str) -> bool:
    """Check if a job with this hash already exists (dedup)."""
    result = session.exec(select(Job).where(Job.seen_hash == seen_hash)).first()
    return result is not None
