from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from otodb_next.models.base import Base


class MediaWork(Base):
	"""Mirror of otodb.models.media.MediaWork.

	TODO(port): READ-ONLY. Status transitions, merge/move, thumbnail handling
	and the delete-cascade set (6 child edges per the migration brief) all
	live Django-side until MediaWork's own write endpoints migrate.
	"""

	__tablename__ = 'otodb_mediawork'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	title: Mapped[str | None] = mapped_column(String(1000))
	description: Mapped[str | None] = mapped_column(Text)
	rating: Mapped[int] = mapped_column(Integer)
	status: Mapped[int] = mapped_column(Integer)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
	_thumbnail: Mapped[str | None] = mapped_column('_thumbnail', String(200))
	moved_to_id: Mapped[int | None] = mapped_column(ForeignKey('otodb_mediawork.id'))
	thumbnail_source_id: Mapped[int | None] = mapped_column(
		ForeignKey('otodb_worksource.id')
	)
