import pytest
from app.worker import process_image
from app.models.task import Task
from app.db.session import SessionLocal
import os
from PIL import Image
import io

def create_test_image():
    """Create a test image file."""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_process_image():
    # Create test image
    test_image = create_test_image()
    image_path = "test.png"
    
    # Save test image
    with open(os.path.join("uploads", image_path), "wb") as f:
        f.write(test_image.getvalue())
    
    # Create task in database
    db = SessionLocal()
    task = Task(
        user_id=1,
        image_path=image_path,
        metadata={
            "resize": (50, 50),
            "grayscale": True
        }
    )
    db.add(task)
    db.commit()
    task_id = task.id
    
    # Process image
    process_image(task_id)
    
    # Check results
    task = db.query(Task).filter(Task.id == task_id).first()
    assert task.status == "completed"
    assert task.result["processed_image"] == f"processed_{image_path}"
    
    # Check if processed image exists
    processed_path = os.path.join("processed", task.result["processed_image"])
    assert os.path.exists(processed_path)
    
    # Check if image was processed correctly
    with Image.open(processed_path) as img:
        assert img.size == (50, 50)
        assert img.mode == "L"  # Grayscale
    
    # Cleanup
    os.remove(os.path.join("uploads", image_path))
    os.remove(processed_path)
    db.delete(task)
    db.commit()
    db.close()

def test_process_image_invalid_task():
    # Try to process non-existent task
    process_image(999999)
    
    # Should not raise any exceptions
    assert True

def test_process_image_invalid_image():
    # Create task with non-existent image
    db = SessionLocal()
    task = Task(
        user_id=1,
        image_path="nonexistent.png",
        metadata={}
    )
    db.add(task)
    db.commit()
    task_id = task.id
    
    # Process image
    process_image(task_id)
    
    # Check results
    task = db.query(Task).filter(Task.id == task_id).first()
    assert task.status == "failed"
    assert task.error is not None
    
    # Cleanup
    db.delete(task)
    db.commit()
    db.close() 