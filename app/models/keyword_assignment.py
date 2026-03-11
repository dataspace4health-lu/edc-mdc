from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from dependencies.database import Base


class KeywordAssignment(Base):
    __tablename__ = "keyword_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword_key: Mapped[str] = mapped_column(
        String(100), ForeignKey("keyword.key"), nullable=False
    )
    organisation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organisations.id"), nullable=False
    )

    keyword: Mapped["Keyword"] = relationship("Keyword", overlaps="keywords")
    organisation: Mapped["Organisation"] = relationship(
        "Organisation", overlaps="keywords"
    )

    __table_args__ = (UniqueConstraint("keyword_key", "organisation_id"),)
