import boto3
from django.conf import settings
from pathlib import Path
from io import BytesIO


class StorageManager:
    """Generic storage manager for CDN or local storage"""

    def __init__(self):
        self.cdn_enabled = settings.OTODB_CDN_ENABLED

        if self.cdn_enabled:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.OTODB_CDN_ENDPOINT_URL,
                aws_access_key_id=settings.OTODB_CDN_ACCESS_KEY,
                aws_secret_access_key=settings.OTODB_CDN_SECRET_KEY,
                region_name='auto'  # Cloudflare R2 uses 'auto'
            )
            self.bucket_name = settings.OTODB_CDN_BUCKET_NAME

    def _is_url(self, path: str) -> bool:
        """
        Simple check to see if path is a URL (we ignore storage ops in these cases)
        """
        return path.lower().startswith(('http://', 'https://'))

    def save(self, file_content: bytes, file_path: str) -> str | None:
        """
        Upload file to CDN or save locally as fallback.
        """
        if self._is_url(file_path):
            print(f"Bypassing storage for URL: {file_path}")
            return file_path

        if self.cdn_enabled:
            try:
                self.s3_client.upload_fileobj(
                    Fileobj=BytesIO(file_content),
                    Bucket=self.bucket_name,
                    Key=file_path.lstrip('/'),
                )
                return file_path
            except Exception as e:
                print(f"CDN upload failed: {e}")
        else:
            return self._save_local(file_content, file_path)

    def _save_local(self, file_content: bytes, file_path: str) -> str | None:
        """Save file to local storage as fallback"""
        if self._is_url(file_path):
            print(f"Bypassing local save for URL: {file_path}")
            return file_path

        # Create media directory if it doesn't exist
        media_root = getattr(settings, 'MEDIA_ROOT', 'media')
        local_path = Path(media_root) / file_path
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with open(local_path, 'wb') as f:
            f.write(file_content)

        return str(local_path.relative_to(media_root))

    def delete(self, file_path: str) -> bool:
        """
        Delete file from CDN or local storage.
        """
        if self._is_url(file_path):
            print(f"Bypassing deletion for URL: {file_path}")
            return True

        if self.cdn_enabled:
            try:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=file_path.lstrip('/')
                )
                return True
            except Exception as e:
                print(f"CDN deletion failed: {e}")
        else:
            try:
                media_root = getattr(settings, 'MEDIA_ROOT', 'media')
                local_path = Path(media_root) / file_path
                if local_path.exists():
                    local_path.unlink()
                    return True
            except Exception as e:
                print(f"Local deletion failed: {e}")

        return False

    def exists(self, file_path: str) -> bool:
        """
        Check if file exists in CDN or local storage.
        """
        if self._is_url(file_path):
            print(f"Bypassing existence check for URL: {file_path}")
            return True

        if self.cdn_enabled:
            try:
                self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=file_path.lstrip('/')
                )
                return True
            except Exception as e:
                print(f"CDN existence check failed: {e}")
        else:
            media_root = getattr(settings, 'MEDIA_ROOT', 'media')
            local_path = Path(media_root) / file_path
            return local_path.exists()

        return False

storage_manager = StorageManager()
