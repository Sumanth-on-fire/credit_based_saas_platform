from PIL import Image
import os
from app.workers.celery_app import celery_app
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.task import Task, TaskStatus

@celery_app.task(name="process_image")
def process_image(task_id: int):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"error": "Task not found"}

        task.status = TaskStatus.PROCESSING
        db.commit()

        # Process the image
        input_path = os.path.join(settings.UPLOAD_FOLDER, task.image_path)
        output_filename = f"processed_{task.image_path}"
        output_path = os.path.join(settings.UPLOAD_FOLDER, output_filename)

        try:
            with Image.open(input_path) as img:
                # Example processing: Convert to grayscale
                processed_img = img.convert('L')
                processed_img.save(output_path)

            task.status = TaskStatus.COMPLETED
            task.result_path = output_filename
            db.commit()

            return {
                "status": "success",
                "result_path": output_filename
            }

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            db.commit()
            return {"error": str(e)}

    finally:
        db.close() 