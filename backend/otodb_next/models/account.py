from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from otodb_next.models.base import Base


class Account(Base):
	"""Mirror of account.Account (AUTH_USER_MODEL).

	TODO(port): READ-ONLY. All account writes (registration, password/reset
	flows, login bookkeeping) stay in Django until auth migrates -- which is
	LAST in the migration order. Do not INSERT/UPDATE/DELETE via this model.
	"""

	__tablename__ = 'account_account'
	__table_args__ = (
		UniqueConstraint('email', name='account_account_email_key'),
		UniqueConstraint('reset_token', name='account_account_reset_token_key'),
		UniqueConstraint('username', name='account_account_username_key'),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	password: Mapped[str] = mapped_column(String(128))
	username: Mapped[str] = mapped_column(String(127))
	email: Mapped[str] = mapped_column(String(255))
	level: Mapped[int] = mapped_column(Integer)
	email_activated: Mapped[bool] = mapped_column(Boolean)
	is_active: Mapped[bool] = mapped_column(Boolean)
	date_created: Mapped[datetime] = mapped_column(DateTime(timezone=True))
	last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	reset_token: Mapped[str | None] = mapped_column(String(127))
