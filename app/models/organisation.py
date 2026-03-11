from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from dependencies.database import Base
from models.contact import Contact
from typing import List, Optional, Set
from models.user_assignment import UserOrganisationAssignment


class Organisation(Base):
    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    type: Mapped[Optional[str]] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String)
    is_deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    category: Mapped[Optional[str]] = mapped_column(String)
    accessible_within_ctie: Mapped[Optional[bool]] = mapped_column(Boolean)

    contacts: Mapped[List[Contact]] = relationship(
        "Contact", back_populates="organisation", cascade="all, delete-orphan"
    )

    qualified_dataset_attributions: Mapped[List["DatasetQualifiedAttribution"]] = (
        relationship(
            "DatasetQualifiedAttribution",
            back_populates="organisation",
            cascade="all, delete-orphan",
        )
    )

    user_assignments: Mapped[Set[UserOrganisationAssignment]] = relationship(
        "UserOrganisationAssignment",
        collection_class=set,
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    keywords: Mapped[Set["Keyword"]] = relationship(
        "Keyword",
        secondary="keyword_assignments",
        back_populates="organisations",
    )

    def __eq__(self, other):
        if not isinstance(other, Organisation):
            return False
        return (
            self.name == other.name
            and self.type == other.type
            and self.email == other.email
            and self.is_deprecated == other.is_deprecated
            and self.category == other.category
            and self.accessible_within_ctie == other.accessible_within_ctie
        )

    def __hash__(self):
        return hash(
            (
                self.name,
                self.type,
                self.email,
                self.is_deprecated,
                self.category,
                self.accessible_within_ctie,
            )
        )

    def to_dict_for_diff(self):
        return {
            "name": self.name,
            "type": self.type,
            "email": self.email,
            "is_deprecated": self.is_deprecated,
            "category": self.category,
            "accessible_within_ctie": self.accessible_within_ctie,
        }
