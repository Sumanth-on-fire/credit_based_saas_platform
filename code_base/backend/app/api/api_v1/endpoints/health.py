from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
import redis
import psycopg2
from celery import Celery

router = APIRouter()

def check_database(db: Session) -> bool:
    """Check database connection."""
    try:
        db.execute("SELECT 1")
        return True
    except Exception:
        return False

def check_redis() -> bool:
    """Check Redis connection."""
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD
        )
        return r.ping()
    except Exception:
        return False

def check_celery() -> bool:
    """Check Celery connection."""
    try:
        celery_app = Celery(
            "worker",
            broker=settings.CELERY_BROKER_URL,
            backend=settings.CELERY_RESULT_BACKEND
        )
        return celery_app.control.inspect().active() is not None
    except Exception:
        return False

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Check the health of all services."""
    db_status = check_database(db)
    redis_status = check_redis()
    celery_status = check_celery()

    status = "healthy" if all([db_status, redis_status, celery_status]) else "unhealthy"

    return {
        "status": status,
        "services": {
            "database": "healthy" if db_status else "unhealthy",
            "redis": "healthy" if redis_status else "unhealthy",
            "celery": "healthy" if celery_status else "unhealthy"
        }
    }

@router.get("/health/database")
async def database_health(db: Session = Depends(get_db)):
    """Check database health."""
    return {"status": "healthy" if check_database(db) else "unhealthy"}

@router.get("/health/redis")
async def redis_health():
    """Check Redis health."""
    return {"status": "healthy" if check_redis() else "unhealthy"}

@router.get("/health/celery")
async def celery_health():
    """Check Celery health."""
    return {"status": "healthy" if check_celery() else "unhealthy"} 