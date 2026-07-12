from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
	BigInteger,
	Boolean,
	CheckConstraint,
	DateTime,
	ForeignKey,
	Integer,
	UniqueConstraint,
	func,
)
from sqlalchemy.orm import Mapped, mapped_column

from otodb_next.models.base import Base


class Subscription(Base):
	"""Mirror of otodb.models.posts.Subscription. Written by the revision
	commit path (auto-subscribe on edit, unsubscribe-on-notify).
	"""

	__tablename__ = 'otodb_subscription'
	__table_args__ = (
		UniqueConstraint(
			'subscriber_id', 'entity_type_id', 'entity_id', name='unique_subscription'
		),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	subscriber_id: Mapped[int] = mapped_column(ForeignKey('account_account.id'))
	entity_type_id: Mapped[int] = mapped_column(ForeignKey('django_content_type.id'))
	entity_id: Mapped[int] = mapped_column(BigInteger)


class Notification(Base):
	"""Mirror of otodb.models.posts.Notification. The revision commit path only
	ever writes revision notifications (comment_id/threadpost_id stay NULL).

	TODO(port): comment_id/threadpost_id are plain columns with no
	FK/relationship declared because XtdComment and ThreadPost are not ported
	(the DB still enforces the real FK constraints). Declare them when
	comment/thread endpoints migrate.
	"""

	__tablename__ = 'otodb_notification'
	__table_args__ = (
		CheckConstraint(
			'comment_id IS NULL AND revision_id IS NOT NULL AND threadpost_id IS NULL'
			' OR comment_id IS NOT NULL AND revision_id IS NULL AND threadpost_id IS NULL'
			' OR comment_id IS NULL AND revision_id IS NULL AND threadpost_id IS NOT NULL',
			name='notification_union',
		),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	target_id: Mapped[int] = mapped_column(ForeignKey('account_account.id'))
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=func.now()
	)
	dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
	reason: Mapped[int] = mapped_column(Integer, default=0)  # NotificationReason.REPLY
	revision_id: Mapped[int | None] = mapped_column(ForeignKey('otodb_revision.id'))
	# TODO(port): no FK -- XtdComment not ported; DB enforces the constraint
	comment_id: Mapped[int | None] = mapped_column(Integer)
	# TODO(port): no FK -- ThreadPost not ported; DB enforces the constraint
	threadpost_id: Mapped[int | None] = mapped_column(BigInteger)
