from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Boolean,
    DateTime,
    Text,
    UniqueConstraint,
)
from models.authentic_source_label import AuthenticSourceLabel
from sqlalchemy.orm import relationship, Mapped, mapped_column
from dependencies.database import Base
from typing import Dict, Optional, List
from datetime import datetime, timezone


class AuthenticSourceAssignment(Base):
    __tablename__ = "authentic_source_assignment"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    data_dictionary_entry_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("data_dictionary_entry.id"), nullable=False, index=True
    )
    authentic_source_label_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("authentic_source_label.id"), nullable=False, index=True
    )
    assigned_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
    # Relationships
    data_dictionary_entry: Mapped["DataDictionaryEntry"] = relationship(
        "DataDictionaryEntry",
        foreign_keys=[data_dictionary_entry_id],
        back_populates="authentic_source_assignments",
    )
    label: Mapped["AuthenticSourceLabel"] = relationship(
        "AuthenticSourceLabel",
        foreign_keys=[authentic_source_label_id],
    )
    assigned_by_user: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[assigned_by], back_populates=None
    )
