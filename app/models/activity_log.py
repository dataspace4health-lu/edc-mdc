from datetime import UTC, datetime
from typing import Optional

from dependencies.database import Base
from models.user import User
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ActivityLog(Base):
    __tablename__ = "activity_log"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    action_type: Mapped[str] = mapped_column(
        String, index=True
    )  # e.g., "create", "update"
    entity_type: Mapped[str] = mapped_column(
        String, index=True
    )  # e.g., "dataset", "distribution"
    entity_id: Mapped[str] = mapped_column(String)
    changes: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(UTC)
    )
    user: Mapped[Optional[User]] = relationship(User)
