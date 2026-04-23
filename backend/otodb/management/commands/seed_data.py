"""
Development seed data command.

Populates the database with sample data for local development.
This command is idempotent — re-running it will not create duplicates.

Usage:
    python manage.py seed_data
    python manage.py seed_data --dry-run
"""

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from otodb.account.models import Account
from otodb.models.enums import (
	MimeType,
	Platform,
	Rating,
	WorkOrigin,
	WorkStatus,
	WorkTagCategory,
)
from otodb.models.media import MediaWork, TagWorkInstance
from otodb.models.tag import TagWork
from otodb.models.work_source import WorkSource

ACCOUNTS = [
	{
		'username': 'member1',
		'email': 'member1@example.com',
		'password': 'password',
		'level': Account.Levels.MEMBER,
	},
	{
		'username': 'member2',
		'email': 'member2@example.com',
		'password': 'password',
		'level': Account.Levels.MEMBER,
	},
	{
		'username': 'editor1',
		'email': 'editor1@example.com',
		'password': 'password',
		'level': Account.Levels.EDITOR,
	},
	{
		'username': 'editor2',
		'email': 'editor2@example.com',
		'password': 'password',
		'level': Account.Levels.EDITOR,
	},
]

TAGS = [
	{
		'name': 'ドナルド・マクドナルド',
		'category': WorkTagCategory.SOURCE,
	},
	{
		'name': 'みくる',
		'category': WorkTagCategory.CREATOR,
	},
]

WORKS = [
	{
		'id': 1,
		'title': 'M.C.ドナルドはダンスに夢中なのか？最終鬼畜道化師ドナルド・Ｍ',
		'description': 'ドナルド300万再生おめでとう',
		'rating': Rating.GENERAL,
		'tags': ['ドナルド・マクドナルド', 'みくる'],
	},
]

SOURCES = [
	{
		'work_id': 1,
		'added_by_username': 'editor1',
		'platform': Platform.NICONICO,
		'source_id': 'sm2057168',
		'url': 'https://nicovideo.jp/watch/sm2057168',
		'published_date': '2008-01-17',
		'work_origin': WorkOrigin.AUTHOR,
		'work_status': WorkStatus.AVAILABLE,
		'work_width': 512,
		'work_height': 384,
		'work_duration': 318,
		'title': 'M.C.ドナルドはダンスに夢中なのか？最終鬼畜道化師ドナルド・Ｍ',
		'description': 'ドナルド300万再生おめでとう',
		'thumbnail_url': 'https://img.cdn.nimg.jp/s/nicovideo/thumbnails/2057168/2057168.original/r1280x720l?key=64c3379f18890e6747830c596be0a7276dab4e0fe574a98671b3b0c58c1f54c8',
		'thumbnail_mime': MimeType.JPEG,
		'uploader_id': '921777',
		'set_as_thumbnail': True,
	},
]


# ---------------------------------------------------------------------------


class Command(BaseCommand):
	help = 'Seed the database with sample development data'

	def add_arguments(self, parser):
		parser.add_argument(
			'--dry-run',
			action='store_true',
			help='Show what would be created without writing to the database',
		)

	def handle(self, *args, **options):
		dry_run = options['dry_run']

		if dry_run:
			self.stdout.write(self.style.WARNING('DRY RUN — no changes will be made'))

		try:
			with transaction.atomic():
				self._seed_accounts(dry_run)
				self._seed_tags(dry_run)
				self._seed_works(dry_run)
				self._seed_sources(dry_run)

				if dry_run:
					raise _RollbackDryRun

		except _RollbackDryRun:
			self.stdout.write(self.style.WARNING('Rolled back (dry run)'))

		self.stdout.write(self.style.SUCCESS('Done'))

	# ------------------------------------------------------------------

	def _seed_accounts(self, dry_run: bool) -> None:
		for data in ACCOUNTS:
			username = data['username']
			exists = Account.objects.filter(username=username).exists()
			if exists:
				self.stdout.write(f'  account already exists: {username}')
				continue
			self.stdout.write(f'  create account: {username}')
			if not dry_run:
				Account.objects.create(
					username=username,
					email=data['email'],
					password=make_password(data['password']),
					level=data.get('level', Account.Levels.MEMBER),
				)

	def _seed_tags(self, dry_run: bool) -> None:
		for data in TAGS:
			name = data['name']
			exists = TagWork.objects.filter(name=name).exists()
			if exists:
				self.stdout.write(f'  tag already exists: {name}')
				continue
			self.stdout.write(f'  create tag: {name}')
			if not dry_run:
				TagWork.objects.create(
					name=name,
					category=data.get('category', WorkTagCategory.UNCATEGORIZED),
				)

	def _seed_works(self, dry_run: bool) -> None:
		for data in WORKS:
			kwargs = {'rating': data.get('rating', Rating.GENERAL)}
			if 'id' in data:
				kwargs['id'] = data['id']
			if 'title' in data:
				kwargs['title'] = data['title']
			if 'description' in data:
				kwargs['description'] = data['description']

			work_id = data.get('id')
			if work_id and MediaWork.objects.filter(pk=work_id).exists():
				self.stdout.write(f'  work already exists: id={work_id}')
				continue

			self.stdout.write(f'  create work: id={work_id}')
			if not dry_run:
				work = MediaWork.objects.create(**kwargs)
				for tag_name in data.get('tags', []):
					try:
						tag = TagWork.objects.get(name=tag_name)
						TagWorkInstance.objects.get_or_create(work=work, work_tag=tag)
					except TagWork.DoesNotExist:
						self.stdout.write(
							self.style.WARNING(
								f'    tag not found, skipping: {tag_name}'
							)
						)

	def _seed_sources(self, dry_run: bool) -> None:
		for data in SOURCES:
			url = data['url']
			exists = WorkSource.objects.filter(url=url).exists()
			if exists:
				self.stdout.write(f'  source already exists: {url}')
				continue
			self.stdout.write(f'  create source: {url}')
			if not dry_run:
				added_by = Account.objects.get(username=data['added_by_username'])
				source = WorkSource.objects.create(
					media_id=data['work_id'],
					added_by=added_by,
					platform=data['platform'],
					source_id=data.get('source_id'),
					url=url,
					published_date=data.get('published_date'),
					work_origin=data.get('work_origin', WorkOrigin.AUTHOR),
					work_status=data.get('work_status', WorkStatus.AVAILABLE),
					work_width=data.get('work_width'),
					work_height=data.get('work_height'),
					work_duration=data.get('work_duration'),
					title=data.get('title'),
					description=data.get('description'),
					thumbnail_url=data.get('thumbnail_url'),
					thumbnail_mime=data.get('thumbnail_mime'),
					thumbnail_hash=data.get('thumbnail_hash'),
					uploader_id=data.get('uploader_id'),
				)
				if data.get('set_as_thumbnail'):
					MediaWork.objects.filter(pk=data['work_id']).update(
						thumbnail_source=source
					)


class _RollbackDryRun(Exception):
	"""Raised inside a transaction to trigger a rollback at the end of a dry run."""
