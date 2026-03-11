from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from dependencies.database import Base


class ApplicableLegislationAssignment(Base):
    __tablename__ = "applicable_legislation_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    applicable_legislation_key: Mapped[str] = mapped_column(
        String(100), ForeignKey("applicable_legislation.key"), nullable=False
    )
    organisation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organisations.id"), nullable=False
    )

    applicable_legislation: Mapped["ApplicableLegislation"] = relationship(
        "ApplicableLegislation", overlaps="organisations"
    )
    organisation: Mapped["Organisation"] = relationship(
        "Organisation", overlaps="organisations"
    )

    __table_args__ = (
        UniqueConstraint("applicable_legislation_key", "organisation_id"),
    )
