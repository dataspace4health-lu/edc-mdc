from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from dependencies.database import Base
from typing import Dict, Optional


class DatasetRelation(Base):
    __tablename__ = "dataset_relation"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    source_dataset: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dataset.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_dataset: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("dataset.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    relation_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    external_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    external_role: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source: Mapped["Dataset"] = relationship(
        "Dataset", foreign_keys=[source_dataset], back_populates="source_relations"
    )
    target: Mapped[Optional["Dataset"]] = relationship(
        "Dataset", foreign_keys=[target_dataset], back_populates="target_relations"
    )

    @property
    def is_dataset_relation(self) -> bool:
        return self.target_dataset is not None

    @property
    def is_external_relation(self) -> bool:
        return self.external_url is not None

    def to_dict_for_diff(self) -> Dict:
        result = {"source_dataset": self.source_dataset}
        if self.is_dataset_relation:
            result.update(
                {
                    "target_dataset": self.target_dataset,
                    "relation_type": self.relation_type,
                }
            )
        else:
            result.update(
                {
                    "external_url": self.external_url,
                    "external_role": self.external_role,
                    "external_description": self.external_description,
                }
            )
        return result
