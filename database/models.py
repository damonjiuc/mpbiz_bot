from typing import Optional

from sqlalchemy import DateTime, String, Text, Integer, Boolean, func, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    phone: Mapped[int] = mapped_column(Integer, nullable=False)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    user_name: Mapped[str] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(16), default='user', nullable=False)
    generations_left: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    bonus_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bonus_left: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    selected_store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("store.id", ondelete="SET NULL"), nullable=True)

    user_stores: Mapped[list["Store"]] = relationship(
        "Store",
        foreign_keys="[Store.tg_id]",
        back_populates="user",
        primaryjoin="User.tg_id == Store.tg_id")
    selected_store: Mapped[Optional["Store"]] = relationship(
        "Store",
        foreign_keys=[selected_store_id],
    )
    user_reports: Mapped[list["Report"]] = relationship("Report", back_populates="user")
    user_payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user")
    referred_by: Mapped[list["Ref"]] = relationship(
        "Ref", foreign_keys="[Ref.referral_id]", back_populates="referral"
    )
    referrals: Mapped[list["Ref"]] = relationship(
        "Ref", foreign_keys="[Ref.referrer_id]", back_populates="referrer"
    )


class Store(Base):
    __tablename__ = 'store'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    token: Mapped[str] = mapped_column(String(512), nullable=False)

    store_reports: Mapped[list["Report"]] = relationship("Report", back_populates="store")
    user: Mapped["User"] = relationship("User", back_populates="user_stores", foreign_keys=[tg_id])


class Report(Base):
    __tablename__ = 'report'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"), nullable=False)
    date_of_week: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    report_path: Mapped[str] = mapped_column(String, nullable=False)
    store_id: Mapped[int] = mapped_column(ForeignKey("store.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_reports")
    store: Mapped["Store"] = relationship("Store", back_populates="store_reports")


class Ref(Base):
    __tablename__ = 'ref'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    referral_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"), nullable=False, unique=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"), nullable=False)

    referrer: Mapped["User"] = relationship(
        "User", foreign_keys=[referrer_id], back_populates="referrals"
    )
    referral: Mapped["User"] = relationship(
        "User", foreign_keys=[referral_id], back_populates="referred_by"
    )

    __table_args__ = (
        Index('idx_referral_unique', 'referral_id', unique=True),  # явное указание индекса
    )


class Payment(Base):
    __tablename__ = 'payment'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    generations_num: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_payments")


class Article(Base):
    __tablename__ = 'article'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    show: Mapped[bool] = mapped_column(Boolean, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    img_path: Mapped[str] = mapped_column(String)
