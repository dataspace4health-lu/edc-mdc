from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from dependencies.database import Base
from typing import Dict


class DatasetQualifiedAttribution(Base):
    __tablename__ = "dataset_qualified_attribution"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(String, nullable=False)
    organisation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organisations.id", ondelete="CASCADE")
    )

    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="qualified_attributions"
    )
    organisation: Mapped["Organisation"] = relationship(
        "Organisation", back_populates="qualified_dataset_attributions"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetQualifiedAttribution):
            return False
        return (
            self.organisation_id == other.organisation_id
            and self.role == other.role
            and self.dataset_id == other.dataset_id
        )

    def __hash__(self):
        return hash((self.organisation_id, self.role, self.dataset_id))

    def to_dict_for_diff(self) -> Dict[str, any]:
        return {
            "organisation_id": self.organisation_id,
            "role": self.role,
        }
