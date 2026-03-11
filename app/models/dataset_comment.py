from datetime import datetime
from typing import Optional, Set
from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from dependencies.database import Base


class DatasetComment(Base):
    __tablename__ = "dataset_comments"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    dataset: Mapped["Dataset"] = relationship(
        "Dataset", foreign_keys=[dataset_id], back_populates="dataset_comments"
    )
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="dataset_comments"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "user_id": self.user_id,
            "content": self.content,
        }
