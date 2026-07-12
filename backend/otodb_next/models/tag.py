from __future__ import annotations

from sqlalchemy import (
	BigInteger,
	Boolean,
	ForeignKey,
	Integer,
	String,
	UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from otodb_next.models.base import Base


class TagWork(Base):
	"""Mirror of otodb.models.tag.TagWork.

	TODO(port): READ-ONLY until TagWork's write endpoints migrate, because:
	- tagulous owns its write behavior Python-side in Django (slug
	  generation, count maintenance, merge logic);
	- the delete-cascade relationship set (10 child edges per the migration
	  brief) is NOT declared yet -- it must be generated from Django meta
	  before session.delete() on a TagWork is allowed.
	Do not create/update/delete TagWork rows via this model.
	"""

	__tablename__ = 'otodb_tagwork'
	__table_args__ = (
		UniqueConstraint('name', name='otodb_tagwork_name_key'),
		UniqueConstraint('slug', name='otodb_tagwork_slug_b63a3444_uniq'),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	name: Mapped[str] = mapped_column(String(255))
	slug: Mapped[str] = mapped_column(String(255))
	count: Mapped[int] = mapped_column(Integer, default=0)
	protected: Mapped[bool] = mapped_column(Boolean, default=False)
	category: Mapped[int] = mapped_column(Integer, default=0)  # UNCATEGORIZED
	deprecated: Mapped[bool] = mapped_column(Boolean, default=False)
	aliased_to_id: Mapped[int | None] = mapped_column(ForeignKey('otodb_tagwork.id'))
	media_type: Mapped[int | None] = mapped_column(Integer)

	aliased_to: Mapped[TagWork | None] = relationship(
		'TagWork', remote_side='TagWork.id'
	)


class TagWorkConnection(Base):
	"""Mirror of otodb.models.connection.TagWorkConnection -- the revision-port
	spike model (RevisionMeta: tracked_fields=[tag, site, content_id],
	entity_attrs=[tag]).
	"""

	# Identical to Django's RevisionMeta; everything else is derived from the
	# mapper by revisions.init_tracking()
	__revision__ = {
		'tracked_fields': ['tag', 'site', 'content_id'],
		'entity_attrs': ['tag'],
	}

	__tablename__ = 'otodb_tagworkconnection'
	__table_args__ = (
		UniqueConstraint(
			'tag_id',
			'site',
			'content_id',
			name='otodb_tagworkconnection_tag_id_site_content_id_98dc8971_uniq',
		),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	tag_id: Mapped[int] = mapped_column(ForeignKey('otodb_tagwork.id'))
	site: Mapped[int] = mapped_column(Integer)
	content_id: Mapped[str] = mapped_column(String(1000))

	tag: Mapped[TagWork] = relationship(TagWork)
