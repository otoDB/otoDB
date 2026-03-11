import re
import logging
import boto3
from django.conf import settings
from pathlib import Path
from io import BytesIO

logger = logging.getLogger(__name__)


class StorageManager:
	"""Generic storage manager for CDN or local storage"""

	def __init__(self):
		self.cdn_enabled: bool = settings.OTODB_CDN_ENABLED
		self.cdn_root: str = settings.OTODB_CDN_ROOT

		self.media_path: Path = settings.MEDIA_ROOT

		if self.cdn_enabled:
			self.s3_client = boto3.client(
				's3',
				endpoint_url=settings.OTODB_CDN_ENDPOINT_URL,
				aws_access_key_id=settings.OTODB_CDN_ACCESS_KEY,
				aws_secret_access_key=settings.OTODB_CDN_SECRET_KEY,
				region_name='auto',  # Cloudflare R2 uses 'auto'
			)
			self.bucket_name = settings.OTODB_CDN_BUCKET_NAME
		else:
			if not self.media_path or not settings.MEDIA_URL:
				raise ValueError(
					'MEDIA_ROOT or MEDIA_URL is not set in Django settings'
				)
			self.media_path.parent.mkdir(parents=True, exist_ok=True)

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
			logger.debug(f'Bypassing storage for URL: {file_path}')
			return file_path

		if self.cdn_enabled:
			try:
				self.s3_client.upload_fileobj(
					Fileobj=BytesIO(file_content),
					Bucket=self.bucket_name,
					Key=re.sub(r'/+', '/', self.cdn_root + file_path).lstrip('/'),
					ExtraArgs={
						'CacheControl': 'public, max-age=31536000, immutable',
					},
				)
				return file_path
			except Exception as e:
				logger.error(f'CDN upload failed: {e}')
		else:
			return self._save_local(file_content, file_path)

	def _save_local(self, file_content: bytes, file_path: str) -> str | None:
		"""Save file to local storage as fallback"""
		if self._is_url(file_path):
			logger.debug(f'Bypassing local save for URL: {file_path}')
			return file_path

		local_path = self.media_path / file_path.lstrip('/')
		local_path.parent.mkdir(parents=True, exist_ok=True)

		with open(local_path, 'wb') as f:
			f.write(file_content)

		return file_path

	def delete(self, file_path: str) -> bool:
		"""
		Delete file from CDN or local storage.
		"""
		if self._is_url(file_path):
			logger.debug(f'Bypassing deletion for URL: {file_path}')
			return True

		if self.cdn_enabled:
			try:
				self.s3_client.delete_object(
					Bucket=self.bucket_name,
					Key=re.sub(r'/+', '/', self.cdn_root + file_path).lstrip('/'),
				)
				return True
			except Exception as e:
				logger.error(f'CDN deletion failed: {e}')
		else:
			try:
				local_path = self.media_path / file_path.lstrip('/')
				if local_path.exists():
					local_path.unlink()
					return True
			except Exception as e:
				logger.error(f'Local deletion failed: {e}')

		return False

	def read(self, file_path: str) -> bytes | None:
		"""
		Read file content from CDN or local storage.
		"""
		if self._is_url(file_path):
			logger.warning(f'Cannot read URL directly: {file_path}')
			return None

		if self.cdn_enabled:
			try:
				response = self.s3_client.get_object(
					Bucket=self.bucket_name,
					Key=re.sub(r'/+', '/', self.cdn_root + file_path).lstrip('/'),
				)
				return response['Body'].read()
			except Exception as e:
				logger.warning(f'CDN read failed: {e}')
		else:
			try:
				local_path = self.media_path / file_path.lstrip('/')
				if local_path.exists():
					with open(local_path, 'rb') as f:
						return f.read()
			except Exception as e:
				logger.error(f'Local read failed: {e}')

		return None

	def exists(self, file_path: str) -> bool:
		"""
		Check if file exists in CDN or local storage.
		"""
		if self._is_url(file_path):
			logger.debug(f'Bypassing existence check for URL: {file_path}')
			return True

		if self.cdn_enabled:
			try:
				self.s3_client.head_object(
					Bucket=self.bucket_name,
					Key=re.sub(r'/+', '/', self.cdn_root + file_path).lstrip('/'),
				)
				return True
			except Exception as e:
				logger.debug(f'CDN existence check failed: {e}')
		else:
			local_path = self.media_path / file_path.lstrip('/')
			return local_path.exists()

		return False

	def url(self, file_path: str) -> str:
		"""
		Get the URL of the file in CDN or local storage.
		"""
		if self._is_url(file_path):
			return file_path

		if file_path and settings.OTODB_CDN_ENABLED:
			return (
				settings.OTODB_CDN_HOST
				+ settings.OTODB_CDN_ROOT
				+ file_path.lstrip('/')
			)
		elif file_path and self.exists(file_path):
			# Fallback to local storage
			return settings.MEDIA_URL + file_path.lstrip('/')

		return ''


storage_manager = StorageManager()
