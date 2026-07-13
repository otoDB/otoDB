from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
	BigInteger,
	Boolean,
	CheckConstraint,
	Date,
	DateTime,
	ForeignKey,
	Integer,
	String,
	Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from otodb_next.models.base import Base
from otodb_next.models.media import MediaWork


class WorkSource(Base):
	"""Mirror of otodb.models.work_source.WorkSource.

	TODO(port): field updates are live (source/origin endpoint); creation
	(defaults + thumbnail pipeline), refresh and deletion stay Django-side --
	deletes additionally need the MediaWork.thumbnail_source SET_NULL edge
	declared before session.delete() is allowed.
	"""

	# Identical to Django's RevisionMeta; everything else is derived from the
	# mapper by revisions.init_tracking()
	__revision__ = {
		'tracked_fields': [
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
		],
		'entity_attrs': ['self', 'media'],
	}

	__tablename__ = 'otodb_worksource'
	__table_args__ = (
		CheckConstraint(
			'work_duration >= 0', name='otodb_worksource_work_duration_check'
		),
		CheckConstraint('work_height >= 0', name='otodb_worksource_work_height_check'),
		CheckConstraint('work_width >= 0', name='otodb_worksource_work_width_check'),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	media_id: Mapped[int | None] = mapped_column(ForeignKey('otodb_mediawork.id'))
	platform: Mapped[int] = mapped_column(Integer)
	source_id: Mapped[str | None] = mapped_column(String(1000))
	url: Mapped[str] = mapped_column(String(200))
	published_date: Mapped[date | None] = mapped_column(Date)
	work_origin: Mapped[int] = mapped_column(Integer)
	work_status: Mapped[int] = mapped_column(Integer)
	work_width: Mapped[int | None] = mapped_column(Integer)
	work_height: Mapped[int | None] = mapped_column(Integer)
	work_duration: Mapped[int | None] = mapped_column(Integer)
	title: Mapped[str | None] = mapped_column(String(1000))
	description: Mapped[str | None] = mapped_column(Text)
	thumbnail_url: Mapped[str | None] = mapped_column(String(200))
	thumbnail_mime: Mapped[int | None] = mapped_column(Integer)
	thumbnail_hash: Mapped[str | None] = mapped_column(String(64))
	uploader_id: Mapped[str | None] = mapped_column(String(1000))
	added_by_id: Mapped[int] = mapped_column(ForeignKey('account_account.id'))
	is_pending: Mapped[bool] = mapped_column(Boolean)
	pending_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

	media: Mapped[MediaWork | None] = relationship(MediaWork, foreign_keys=[media_id])
