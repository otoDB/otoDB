from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from otodb_next.models.base import Base


class ContentType(Base):
	"""Mirror of django_content_type. Rows are created by Django's migration
	machinery; otodb_next only reads them (the revision writer resolves its
	model -> content_type_id map from this table at startup). The table
	outlives Django as plain data -- revision rows reference it forever.

	TODO(port): READ-ONLY while Django exists. At Django cutoff, decide how
	rows for NEW tracked models get inserted (Django's contenttypes machinery
	does it today on migrate).
	"""

	__tablename__ = 'django_content_type'
	__table_args__ = (
		UniqueConstraint(
			'app_label',
			'model',
			name='django_content_type_app_label_model_76bd3d3b_uniq',
		),
	)

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	app_label: Mapped[str] = mapped_column(String(100))
	model: Mapped[str] = mapped_column(String(100))
