from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Set
from dependencies.database import Base


class ApplicableLegislation(Base):
    __tablename__ = "applicable_legislation"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(String)
    link: Mapped[str] = mapped_column(String)
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=True
    )
    created_by: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[created_by_id]
    )
    organisations: Mapped[Set["Organisation"]] = relationship(
        "Organisation",
        secondary="applicable_legislation_assignments",
        overlaps="applicable_legislation,organisation",
    )

    def to_dict_for_diff(self):
        data = {
            "key": self.key,
            "eng_label": self.eng_label,
            "description": self.description,
            "link": self.link,
            "organisation_ids": (
                [org.id for org in self.organisations] if self.organisations else []
            ),
        }
        return data
