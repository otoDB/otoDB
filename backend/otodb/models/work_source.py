from datetime import date, datetime
import logging
from django.db import models
from simple_history.models import HistoricalRecords, HistoricForeignKey
import requests

from .enums import Platform, WorkOrigin, WorkStatus, MimeType
from .media import MediaWork
import hashlib

from otodb.account.models import Account
from otodb.common import video_info, process_video_info, fetch_thumbnail_mime_type
from otodb.storage_manager import storage_manager

logger = logging.getLogger(__name__)


class ActiveManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(rejection__isnull=True)


class WorkSource(models.Model):
	media = HistoricForeignKey(
		MediaWork, on_delete=models.CASCADE, null=True, blank=True
	)
	platform = models.IntegerField(choices=Platform.choices)
	source_id = models.CharField(max_length=1000)

	url = models.URLField(null=False, blank=False)
	published_date = models.DateField(
		auto_now=False, auto_now_add=False, null=True, blank=True
	)
	work_origin = models.IntegerField(
		choices=WorkOrigin.choices, default=WorkOrigin.AUTHOR
	)
	work_status = models.IntegerField(
		choices=WorkStatus.choices, default=WorkStatus.AVAILABLE
	)
	work_width = models.PositiveIntegerField(null=True, blank=True)
	work_height = models.PositiveIntegerField(null=True, blank=True)
	work_duration = models.PositiveIntegerField(null=True, blank=True)

	title = models.CharField(max_length=1000, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	thumbnail_url = models.URLField(null=True, blank=False)
	thumbnail_mime = models.IntegerField(
		choices=MimeType.choices, null=True, blank=True
	)
	thumbnail_hash = models.CharField(max_length=64, null=True, blank=True)
	uploader_id = models.CharField(max_length=1000, null=True, blank=False)

	added_by = models.ForeignKey(
		Account, blank=False, null=False, on_delete=models.CASCADE
	)

	objects = models.Manager()
	active_objects = ActiveManager()
	history = HistoricalRecords()

	info_payload: 'WorkSourceInfoPayload'

	def __str__(self) -> str:
		return f'#{self.media.pk} - {self.url}' if self.media else self.title

	class Meta:
		verbose_name = 'Media Source'
		verbose_name_plural = 'Media Sources'
		ordering = ['work_status', 'work_origin', 'published_date']

	def refresh(self, use_cache=False):
		"""
		Refresh work source information.

		Args:
		    use_cache: If `True`, use previously cached payload instead of requesting new data.
		"""
		full_info = None

		if use_cache and getattr(self, 'info_payload', None):
			info = process_video_info(self.info_payload.payload, self.url)
		else:
			info, full_info = video_info(self.url)

		if info:
			self.title = info['title']
			self.description = info['description']
			self.uploader_id = info['uploader_id']
			self.thumbnail_url = info.get('thumb', self.thumbnail_url)
			self.thumbnail_mime = info.get('thumb_mime', self.thumbnail_mime)
			self.work_width = info.get('work_width', self.work_width)
			self.work_height = info.get('work_height', self.work_height)
			self.work_duration = info.get('work_duration', self.work_duration)

			# Re-upload thumbnail to CDN for non-cached refreshes
			if not use_cache and self.thumbnail_url and self.thumbnail_mime:
				self.save_thumbnail()

			if full_info is not None:
				WorkSourceInfoPayload.objects.update_or_create(
					source=self, defaults={'payload': full_info}
				)

			if self.media:
				from .tag import TagWork

				new_tags = []
				for tag in info.get('tags', []):
					try:
						tag_obj, created = TagWork.objects.get_or_create(name=tag)
						self.media.tags.add(tag_obj)
						if created:
							new_tags.append(tag_obj.pk)
					except Exception:
						tag_obj = TagWork.objects.get(name=tag)
						self.media.tags.add(tag_obj)
				if new_tags:
					self.media.tagworkinstance_set.filter(work_tag__in=new_tags).update(
						instance_imported_from_source=True
					)
		else:
			logger.error(
				f'Failed to refresh WorkSource {self.pk} - {self.url}: No info found.'
			)
			self.work_status = WorkStatus.DOWN

		self.save()

	def save_thumbnail(self) -> bool:
		if not self.thumbnail_mime and self.thumbnail_url:
			self.thumbnail_mime = fetch_thumbnail_mime_type(self.thumbnail_url)
		if not self.thumbnail_url or not self.thumbnail_mime:
			return False
		try:
			response = requests.get(self.thumbnail_url, timeout=10)
			response.raise_for_status()

			self.thumbnail_hash = hashlib.sha256(response.content).hexdigest()
			if storage_manager.exists(self.thumbnail_path):
				self.save(update_fields=['thumbnail_hash'])
				return True

			path = storage_manager.save(response.content, self.thumbnail_path)

			if path:
				self.save(update_fields=['thumbnail_hash'])
				return True
			else:
				logger.error(f'Failed to upload thumbnail for WorkSource {self.pk}')
				return False
		except Exception as e:
			logger.error(f'Error uploading thumbnail for WorkSource {self.pk}: {e}')
			return False

	# Gets the source registered at the url if it exists, otherwise register as pending
	@staticmethod
	def from_url(
		url, user, is_reupload, metadata=None, info=None, full_info=None
	) -> tuple['WorkSource | None', 'dict | None']:
		"""
		Gets or creates a WorkSource from a URL.

		Args:
		    url: The URL to fetch
		    user: The user adding the source
		    is_reupload: Whether this is a reupload (not by original author)
		    metadata: Optional metadata dict for unavailable sources (editors only)
		    info: Optional pre-fetched info dict (for optimization)
		    full_info: Optional pre-fetched full info dict (for optimization)

		Returns:
		    Tuple of (WorkSource, info_dict) or (None, None) if failed
		"""
		from otodb.common import video_info, parse_url_for_platform

		# Try to fetch info if not provided
		if info is None:
			info, full_info = video_info(url, expected_unavailable=metadata is not None)

		# Handle unavailable sources
		if info is None and metadata is not None:
			parsed = parse_url_for_platform(url)
			if parsed is None:
				logger.error(f'Failed to parse URL for platform: {url}')
				return None, None

			# Build minimal info from parsed URL and manual metadata
			from otodb.common import fetch_thumbnail_mime_type

			published_date = metadata.get('published_date') if metadata else None
			thumbnail_url = metadata.get('thumbnail_url') if metadata else None

			# Fetch thumbnail mime type if URL is provided
			thumb_mime = (
				fetch_thumbnail_mime_type(thumbnail_url) if thumbnail_url else None
			)

			info = {
				'site': parsed['platform'],
				'id': parsed['source_id'],
				'url': parsed['canonical_url'],
				'title': metadata.get('title') if metadata else None,
				'description': metadata.get('description') if metadata else '',
				'timestamp': datetime.combine(
					published_date, datetime.min.time()
				).timestamp()
				if published_date
				else None,
				'uploader_id': metadata.get('uploader_id') if metadata else None,
				'thumb': thumbnail_url,
				'thumb_mime': thumb_mime,
				'work_width': metadata.get('work_width') if metadata else None,
				'work_height': metadata.get('work_height') if metadata else None,
				'work_duration': metadata.get('work_duration') if metadata else None,
				'tags': [],
			}
		elif info is None:
			logger.error(f'Failed to get video info for URL: {url}')
			return None, None

		if info['site'] is None:
			return None, None

		# Check if source already exists
		try:
			src = WorkSource.objects.get(platform=info['site'], source_id=info['id'])
		except WorkSource.DoesNotExist:
			# Create new source
			src = WorkSource.objects.create(
				media=None,
				title=info['title'],
				description=info['description'],
				url=info['url'],
				platform=info['site'],
				source_id=info['id'],
				published_date=(
					date.fromtimestamp(info['timestamp']) if info['timestamp'] else None
				),
				work_origin=WorkOrigin(is_reupload),
				work_status=WorkStatus.DOWN
				if metadata is not None
				else WorkStatus.AVAILABLE,
				thumbnail_url=info.get('thumb'),
				thumbnail_mime=info.get('thumb_mime'),
				work_width=info.get('work_width'),
				work_height=info.get('work_height'),
				work_duration=info.get('work_duration'),
				added_by=user,
				uploader_id=info['uploader_id'],
			)

			if full_info is not None:
				WorkSourceInfoPayload.objects.create(source=src, payload=full_info)

			if src.thumbnail_url and src.thumbnail_mime:
				src.save_thumbnail()

		return src, info

	@property
	def thumbnail_path(self) -> str:
		"""
		Returns content-addressed path for thumbnail using two-level directory structure.
		Format: /t/{hash[:2]}/{hash[2:4]}/{hash}.{ext}
		"""
		if not self.thumbnail_hash or not self.thumbnail_mime:
			# REVIEW: This should never be reached but we may want to handle it more safely
			return None
		ext = MimeType.extension(self.thumbnail_mime)
		# Two-level sharding: /t/ab/cd/abcd...hash.ext
		return f'/t/{self.thumbnail_hash[:2]}/{self.thumbnail_hash[2:4]}/{self.thumbnail_hash}.{ext}'

	@property
	def thumbnail(self) -> str:
		"""
		Returns the URL endpoint from which a thumbnail is served.
		"""
		return storage_manager.url(self.thumbnail_path) or self.thumbnail_url  # type: ignore -- Fallback to 3rd-party remote thumbnail URL


class WorkSourceRejection(models.Model):
	source = models.OneToOneField(
		WorkSource, null=False, on_delete=models.CASCADE, related_name='rejection'
	)
	reason = models.CharField(max_length=1000, null=False, blank=False)
	by = models.ForeignKey(Account, blank=False, null=False, on_delete=models.RESTRICT)


class WorkSourceInfoPayload(models.Model):
	source = models.OneToOneField(
		WorkSource,
		blank=False,
		null=False,
		on_delete=models.CASCADE,
		related_name='info_payload',
	)
	payload = models.JSONField(null=False, blank=False)
