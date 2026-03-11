from sqlalchemy import Integer, String, Boolean, DateTime
from typing import Set, Optional
from datetime import datetime
from dependencies.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.dataset_comment import DatasetComment


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    email = mapped_column(String(length=255), nullable=True, unique=True)
    iam_roles: Mapped[str] = mapped_column(String(length=255), nullable=True)
    is_deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    external_id: Mapped[str] = mapped_column(
        String(length=255), nullable=False, unique=True
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dataset_comments: Mapped[Set[DatasetComment]] = relationship(
        "DatasetComment",
        foreign_keys=[DatasetComment.user_id],
        collection_class=set,
        cascade="all, delete-orphan",
    )
    dataset_group_managers: Mapped[Set["DatasetGroupManagers"]] = relationship(
        "DatasetGroupManagers", back_populates="user", collection_class=set
    )
    organisation_assignments: Mapped[Set["UserOrganisationAssignment"]] = relationship(
        "UserOrganisationAssignment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
