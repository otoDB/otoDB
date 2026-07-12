from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
	BigInteger,
	Boolean,
	CheckConstraint,
	DateTime,
	ForeignKey,
	Index,
	Integer,
	String,
	Text,
	UniqueConstraint,
	func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from otodb_next.models.account import Account
from otodb_next.models.base import Base


class Revision(Base):
	"""Mirror of otodb.models.revision.Revision"""

	__tablename__ = 'otodb_revision'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
	message: Mapped[str] = mapped_column(Text, default='')
	user_id: Mapped[int | None] = mapped_column(ForeignKey('account_account.id'))

	user: Mapped[Account | None] = relationship(Account)
	changes: Mapped[list[RevisionChange]] = relationship(
		'RevisionChange', back_populates='rev'
	)


class RevisionChange(Base):
	"""Mirror of otodb.models.revision.RevisionChange"""

	__tablename__ = 'otodb_revisionchange'
	__table_args__ = (
		CheckConstraint(
			'NOT (deleted AND restored)',
			name='revisionchange_cannot_be_both_delete_and_restore',
		),
		UniqueConstraint(
			'rev_id',
			'target_type_id',
			'target_id',
			'target_column',
			name='otodb_revisionchange_rev_id_target_type_id_ta_797dec6f_uniq',
		),
		Index(
			'revisionchange_model_can_only_be_deleted_once',
			'target_type_id',
			'target_id',
			postgresql_where='deleted',
			unique=True,
		),
		Index(
			'revisionchange_model_can_only_be_restored_once',
			'target_type_id',
			'target_id',
			postgresql_where='restored',
			unique=True,
		),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	rev_id: Mapped[int] = mapped_column(ForeignKey('otodb_revision.id'))
	target_type_id: Mapped[int] = mapped_column(ForeignKey('django_content_type.id'))
	target_id: Mapped[int] = mapped_column(BigInteger)
	deleted: Mapped[bool] = mapped_column(Boolean, default=False)
	restored: Mapped[bool] = mapped_column(Boolean, default=False)
	target_column: Mapped[str | None] = mapped_column(String(100))
	target_value: Mapped[str | None] = mapped_column(Text)

	rev: Mapped[Revision] = relationship(Revision, back_populates='changes')
	entities: Mapped[list[RevisionChangeEntity]] = relationship(
		'RevisionChangeEntity', back_populates='change'
	)


class RevisionChangeEntity(Base):
	"""Mirror of otodb.models.revision.RevisionChangeEntity"""

	__tablename__ = 'otodb_revisionchangeentity'
	__table_args__ = (
		UniqueConstraint(
			'change_id',
			'entity_type_id',
			'entity_id',
			name='otodb_revisionchangeenti_change_id_entity_type_id_3b9083a1_uniq',
		),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	change_id: Mapped[int] = mapped_column(ForeignKey('otodb_revisionchange.id'))
	entity_type_id: Mapped[int] = mapped_column(ForeignKey('django_content_type.id'))
	entity_id: Mapped[int] = mapped_column(BigInteger)
	route: Mapped[int] = mapped_column(Integer, default=0)  # Route.UNKNOWN

	change: Mapped[RevisionChange] = relationship(
		RevisionChange, back_populates='entities'
	)
