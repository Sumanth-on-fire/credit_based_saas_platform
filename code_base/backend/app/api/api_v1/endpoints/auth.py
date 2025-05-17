from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password
)
from app.db.session import get_db
from app.models.user import User
from datetime import timedelta

router = APIRouter()

@router.post("/signup")
async def signup(
    email: str,
    password: str,
    full_name: str,
    db: Session = Depends(get_db)
):
    """Create a new user account."""
    # Check if user already exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        credits=0  # Start with 0 credits
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "credits": user.credits
        },
        "token": access_token
    }

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and return access token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "credits": user.credits
        },
        "token": access_token
    } 