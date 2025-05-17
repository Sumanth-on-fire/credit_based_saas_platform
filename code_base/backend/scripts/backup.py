import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import logging
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_database():
    """Backup PostgreSQL database."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("backups/database")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_file = backup_dir / f"backup_{timestamp}.sql"
        
        # Create database backup
        subprocess.run([
            "pg_dump",
            "-h", settings.POSTGRES_SERVER,
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", str(backup_file)
        ], env={"PGPASSWORD": settings.POSTGRES_PASSWORD})
        
        logger.info(f"Database backup created: {backup_file}")
        return True
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return False

def backup_files():
    """Backup uploaded and processed files."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("backups/files")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup uploads
        uploads_backup = backup_dir / f"uploads_{timestamp}"
        if settings.UPLOAD_DIR.exists():
            shutil.copytree(settings.UPLOAD_DIR, uploads_backup)
            logger.info(f"Uploads backup created: {uploads_backup}")
        
        # Backup processed files
        processed_backup = backup_dir / f"processed_{timestamp}"
        if settings.PROCESSED_DIR.exists():
            shutil.copytree(settings.PROCESSED_DIR, processed_backup)
            logger.info(f"Processed files backup created: {processed_backup}")
        
        return True
    except Exception as e:
        logger.error(f"Files backup failed: {e}")
        return False

def cleanup_old_backups(max_age_days=7):
    """Remove backups older than max_age_days."""
    try:
        backup_dir = Path("backups")
        if not backup_dir.exists():
            return
        
        current_time = datetime.now()
        for item in backup_dir.rglob("*"):
            if item.is_file():
                age = current_time - datetime.fromtimestamp(item.stat().st_mtime)
                if age.days > max_age_days:
                    item.unlink()
                    logger.info(f"Removed old backup: {item}")
    except Exception as e:
        logger.error(f"Backup cleanup failed: {e}")

if __name__ == "__main__":
    logger.info("Starting backup process...")
    
    # Create backups
    db_success = backup_database()
    files_success = backup_files()
    
    if db_success and files_success:
        logger.info("Backup completed successfully")
    else:
        logger.error("Backup completed with errors")
    
    # Cleanup old backups
    cleanup_old_backups() 