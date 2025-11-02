from datetime import date
from django.db import models
import requests
import hashlib

from otodb.account.models import Account
from otodb.common import video_info, process_video_info
from otodb.storage_manager import storage_manager


from .revision import RevisionTrackedModel, RevisionTrackedManager
from .enums import Platform, WorkOrigin, WorkStatus, MimeType
from .media import MediaWork


class ActiveManager(RevisionTrackedManager):
	def get_queryset(self):
		return super().get_queryset().filter(rejection__isnull=True)


class WorkSource(RevisionTrackedModel):
	media = models.ForeignKey(
		MediaWork, on_delete=models.CASCADE, null=True, blank=True
	)
	platform = models.IntegerField(choices=Platform.choices)
	source_id = models.CharField(max_length=1000)

	url = models.URLField(null=False, blank=False)
	published_date = models.DateField(auto_now=False, auto_now_add=False)
	work_origin = models.IntegerField(
		choices=WorkOrigin.choices, default=WorkOrigin.AUTHOR
	)
	work_status = models.IntegerField(
		choices=WorkStatus.choices, default=WorkStatus.AVAILABLE
	)
	work_width = models.PositiveIntegerField(null=True, blank=True)
	work_height = models.PositiveIntegerField(null=True, blank=True)
	work_duration = models.PositiveIntegerField(null=True, blank=True)

	title = models.CharField(max_length=1000, null=False, blank=False)
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

	active_objects = ActiveManager()

	revision_tracked_fields = [
		'media',
		'platform',
		'source_id',
		'url',
		'published_date',
		'work_origin',
		'work_status',
		'work_width',
		'work_height',
		'work_duration',
		'title',
		'description',
		'thumbnail_url',
		'thumbnail_mime',
		'thumbnail_hash',
		'uploader_id',
		'added_by',
	]
	revision_entity_attrs = ['self', 'media']

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

				tags = info.get('tags', [])
				exists = TagWork.objects.filter(name__in=tags)
				created = [
					TagWork.objects.create(name=name)
					for name in tags
					if name not in set(exists.values_list('name', flat=True))
				]
				self.media.tags.add(*exists, *created)
				self.media.tagworkinstance_set.filter(work_tag__in=created).update(
					instance_imported_from_source=True
				)
		else:
			print(
				f'Failed to refresh WorkSource {self.pk} - {self.url}: No info found.'
			)
			self.work_status = WorkStatus.DOWN

		self.save()

	def save_thumbnail(self):
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
				print(f'Failed to upload thumbnail for WorkSource {self.pk}')
				return False
		except Exception as e:
			print(f'Error uploading thumbnail for WorkSource {self.pk}: {e}')
			return False

	# Gets the source registered at the url if it exists, otherwise register as pending
	@staticmethod
	def from_url(url, user, is_reupload, info=None, full_info=None):
		if info is None:
			info, full_info = video_info(url)

		if info is None:
			print(f'Failed to get video info for URL: {url}')
			return None

		if info['site'] is None:
			return None

		try:
			src = WorkSource.objects.get(platform=info['site'], source_id=info['id'])
		except WorkSource.DoesNotExist:
			src = WorkSource.objects.create(
				media=None,
				title=info['title'],
				description=info['description'],
				url=info['url'],
				platform=info['site'],
				source_id=info['id'],
				published_date=date.fromtimestamp(info['timestamp']),
				work_origin=WorkOrigin(is_reupload),
				thumbnail_url=info.get('thumb', None),
				thumbnail_mime=info.get('thumb_mime', None),
				work_width=info.get('work_width', None),
				work_height=info.get('work_height', None),
				work_duration=info.get('work_duration', None),
				added_by=user,
				uploader_id=info['uploader_id'],
			)
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
	date = models.DateTimeField(auto_now_add=True, null=False)


class WorkSourceInfoPayload(models.Model):
	source = models.OneToOneField(
		WorkSource,
		blank=False,
		null=False,
		on_delete=models.CASCADE,
		related_name='info_payload',
	)
	payload = models.JSONField(null=False, blank=False)
