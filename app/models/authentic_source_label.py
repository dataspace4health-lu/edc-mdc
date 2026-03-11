from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Boolean,
    DateTime,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from dependencies.database import Base
from typing import Dict, Optional, List
from datetime import datetime, timezone


class AuthenticSourceLabel(Base):
    __tablename__ = "authentic_source_label"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=True
    )
    is_deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Relationships
    creator: Mapped["User"] = relationship(
        "User", foreign_keys=[created_by], back_populates=None
    )
    assignments: Mapped[List["AuthenticSourceAssignment"]] = relationship(
        "AuthenticSourceAssignment",
        back_populates="label",
        cascade="all, delete-orphan",
    )
