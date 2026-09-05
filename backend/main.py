from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.database import create_db_and_tables
from backend.api.routes import router
from backend.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 JobHunt AI starting up...")
    create_db_and_tables()
    print("✅ Database ready")
    yield
    # Shutdown
    print("👋 JobHunt AI shutting down...")


app = FastAPI(
    title="JobHunt AI",
    description="Multi-agent job search system for college students",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "JobHunt AI",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "running"
    }
