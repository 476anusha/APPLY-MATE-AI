"""File storage service supporting Supabase Storage with local filesystem fallback."""
import logging
import os
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

# Base directory for local storage fallback
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
LOCAL_UPLOAD_DIR = BACKEND_DIR / "uploads"


class FileStorageService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
        self.bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "applymate-files")
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

        self.use_supabase = bool(self.supabase_url and self.supabase_key)
        self._supabase_client = None

        if self.use_supabase:
            try:
                from supabase import create_client  # type: ignore

                self._supabase_client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Using Supabase Storage backend")
            except ImportError:
                logger.warning(
                    "supabase package not installed; falling back to local file storage."
                )
                self.use_supabase = False
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Supabase client: {e}; falling back to local file storage."
                )
                self.use_supabase = False

        if not self.use_supabase:
            LOCAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using Local File Storage backend at: {LOCAL_UPLOAD_DIR}")

    async def upload_file(self, file_bytes: bytes, filename: str, folder: str = "resumes") -> str:
        """
        Uploads file bytes to storage and returns a public URL.
        """
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        storage_path = f"{folder}/{unique_name}".strip("/")

        if self.use_supabase and self._supabase_client:
            try:
                # Upload to Supabase bucket
                self._supabase_client.storage.from_(self.bucket).upload(
                    path=storage_path,
                    file=file_bytes,
                    file_options={"cache-control": "3600", "upsert": "false"},
                )
                # Get public url
                url_res = self._supabase_client.storage.from_(self.bucket).get_public_url(
                    storage_path
                )
                return url_res
            except Exception as e:
                logger.error(f"Supabase upload failed: {e}. Falling back to local storage.")

        # Local storage fallback
        dest_dir = LOCAL_UPLOAD_DIR / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / unique_name
        dest_path.write_bytes(file_bytes)

        # Return local file serving URL
        return f"{self.backend_url}/static/uploads/{folder}/{unique_name}"

    async def delete_file(self, file_url: str) -> bool:
        """
        Deletes a file by public URL.
        """
        if not file_url:
            return False

        if self.use_supabase and self._supabase_client and self.supabase_url in file_url:
            try:
                # Extract relative path from Supabase URL
                marker = f"/storage/v1/object/public/{self.bucket}/"
                if marker in file_url:
                    path = file_url.split(marker)[-1]
                    self._supabase_client.storage.from_(self.bucket).remove([path])
                    return True
            except Exception as e:
                logger.error(f"Failed to delete from Supabase storage: {e}")
                return False

        # Local deletion
        try:
            marker = "/static/uploads/"
            if marker in file_url:
                rel_path = file_url.split(marker)[-1]
                local_path = LOCAL_UPLOAD_DIR / rel_path
                if local_path.exists():
                    local_path.unlink()
                    return True
        except Exception as e:
            logger.error(f"Failed to delete local file: {e}")
            return False

        return False


# Singleton instance
file_storage = FileStorageService()
upload_file = file_storage.upload_file
delete_file = file_storage.delete_file
