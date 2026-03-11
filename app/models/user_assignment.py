from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from dependencies.database import Base
from typing import Set


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)


class RoleAssignment(Base):
    __tablename__ = "role_assignment"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    user_organisation_assignment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_organisation_assignment.id", ondelete="CASCADE"),
        index=True,
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("role.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[Role] = relationship("Role")


class UserOrganisationAssignment(Base):
    __tablename__ = "user_organisation_assignment"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    organisation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organisations.id", ondelete="CASCADE"), index=True
    )
    # Use string references for foreign models to avoid circular imports
    user: Mapped["User"] = relationship(
        "User", back_populates="organisation_assignments"
    )
    organisation: Mapped["Organisation"] = relationship(
        "Organisation", back_populates="user_assignments"
    )
    roles: Mapped[Set[RoleAssignment]] = relationship(
        "RoleAssignment", cascade="all, delete-orphan", collection_class=set
    )

    def __eq__(self, other):
        if not isinstance(other, UserOrganisationAssignment):
            return False
        return (
            self.user_id == other.user_id
            and self.organisation_id == other.organisation_id
        )

    def __hash__(self):
        return hash((self.user_id, self.organisation_id))
