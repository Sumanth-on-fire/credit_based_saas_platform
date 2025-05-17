from celery import Celery
from PIL import Image
import os
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.task import Task
from app.core.logging import setup_logging
import logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task
def process_image(task_id: int):
    """Process an image task."""
    try:
        # Get database session
        db = SessionLocal()
        
        # Get task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        # Update task status
        task.status = "processing"
        db.commit()
        
        # Process image
        input_path = os.path.join(settings.UPLOAD_DIR, task.image_path)
        output_path = os.path.join(settings.PROCESSED_DIR, f"processed_{task.image_path}")
        
        # Open image
        with Image.open(input_path) as img:
            # Apply transformations based on metadata
            if task.metadata.get("resize"):
                width, height = task.metadata["resize"]
                img = img.resize((width, height))
            
            if task.metadata.get("grayscale"):
                img = img.convert("L")
            
            if task.metadata.get("rotate"):
                img = img.rotate(task.metadata["rotate"])
            
            # Save processed image
            img.save(output_path)
        
        # Update task status and result
        task.status = "completed"
        task.result = {"processed_image": f"processed_{task.image_path}"}
        db.commit()
        
        logger.info(f"Task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        if task:
            task.status = "failed"
            task.error = str(e)
            db.commit()
    finally:
        db.close() 