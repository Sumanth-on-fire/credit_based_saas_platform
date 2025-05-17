from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.core.security import get_current_user
from app.workers.tasks import process_image
import os
import json

router = APIRouter()

@router.post("/")
async def create_task(
    image: UploadFile = File(...),
    metadata: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new image processing task."""
    if current_user.credits < settings.MIN_CREDITS_FOR_TASK:
        raise HTTPException(
            status_code=400,
            detail="Not enough credits to process image"
        )

    # Save uploaded file
    file_path = f"{current_user.id}_{image.filename}"
    file_location = os.path.join(settings.UPLOAD_FOLDER, file_path)
    
    with open(file_location, "wb+") as file_object:
        file_object.write(await image.read())

    # Create task record
    task = Task(
        user_id=current_user.id,
        image_path=file_path,
        metadata=metadata,
        credits_used=settings.CREDITS_PER_TASK
    )
    db.add(task)
    
    # Deduct credits
    current_user.credits -= settings.CREDITS_PER_TASK
    db.commit()

    # Start processing
    process_image.delay(task.id)

    return task

@router.get("/")
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for the current user."""
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks

@router.get("/{task_id}")
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task 