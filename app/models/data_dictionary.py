from sqlalchemy import String, Integer, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from dependencies.database import Base
from typing import Dict, Optional, List
from models.authentic_source_assignment import AuthenticSourceAssignment


class DataDictionaryEntry(Base):
    __tablename__ = "data_dictionary_entry"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    field_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    data_type: Mapped[str] = mapped_column(String, nullable=False)
    personally_identifiable_variable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True
    )
    required: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    max_allowed_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_allowed_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    variable_unit: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    allowed_values: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    allowed_values_description: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    table_name: Mapped[str] = mapped_column(String, nullable=False)
    is_authentic_source: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=False, default=False
    )
    privacy_risk_type: Mapped[str] = mapped_column(String, nullable=True)
    position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id"), nullable=False
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", foreign_keys=[dataset_id], back_populates="data_dictionaries"
    )
    authentic_source_assignments: Mapped[List["AuthenticSourceAssignment"]] = (
        relationship(
            "AuthenticSourceAssignment",
            foreign_keys="AuthenticSourceAssignment.data_dictionary_entry_id",
            back_populates="data_dictionary_entry",
            cascade="all, delete-orphan",
        )
    )

    def to_dict_for_diff(self) -> Dict[str, str]:
        return {
            "field_name": self.field_name,
            "description": self.description,
            "data_type": self.data_type,
            "personally_identifiable_variable": self.personally_identifiable_variable
            or False,
            "required": self.required or False,
            "max_allowed_value": self.max_allowed_value or None,
            "min_allowed_value": self.min_allowed_value or None,
            "variable_unit": self.variable_unit or None,
            "allowed_values": self.allowed_values or None,
            "allowed_values_description": self.allowed_values_description or None,
            "table_name": self.table_name,
            "is_authentic_source": self.is_authentic_source or False,
            "privacy_risk_type": self.privacy_risk_type,
        }
