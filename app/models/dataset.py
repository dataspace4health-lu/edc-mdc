from datetime import date, datetime
from enum import Enum
from typing import Set, Optional, List

from dependencies.database import Base
from models.contact import Contact
from models.data_dictionary import DataDictionaryEntry
from models.qualified_attribution import DatasetQualifiedAttribution
from models.dataset_comment import DatasetComment
from models.dataset_relation import DatasetRelation
from models.distribution import Distribution
from models.language import Language
from models.applicable_legislation import ApplicableLegislation
from models.organisation import Organisation
from models.spatial_coverage import SpatialCoverage

# has to import user first to avoid could not find table 'user' with which to generate a foreign key to target column 'id'
from models.user import User
from models.keyword_assignment import KeywordAssignment
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DatasetStatus(Enum):
    DRAFT = "DRAFT"
    COMPLETED = "COMPLETED"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    INTERNAL_ONLY = "INTERNAL_ONLY"
    DEPRECATED = "DEPRECATED"


class DatasetVersionChangeType(Enum):
    METADATA_ONLY = "METADATA_ONLY"
    UNDERLYING_DATA = "UNDERLYING_DATA"


class DatasetType(Base):
    __tablename__ = "dataset_type"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String)


class Periodicity(Base):
    __tablename__ = "periodicity"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String)


class Theme(Base):
    __tablename__ = "theme"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String, nullable=True)


class Keyword(Base):
    __tablename__ = "keyword"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String(500))
    parent_key: Mapped[str] = mapped_column(
        String, ForeignKey("keyword.key"), nullable=True
    )
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=True
    )
    created_by: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[created_by_id]
    )
    organisations: Mapped[Set["Organisation"]] = relationship(
        "Organisation",
        secondary=KeywordAssignment.__table__,
        back_populates="keywords",
        overlaps="keyword,organisation",
    )

    def to_dict_for_diff(self):
        data = {
            "key": self.key,
            "eng_label": self.eng_label,
            "parent_key": self.parent_key,
            "organisation_ids": (
                [org.id for org in self.organisations] if self.organisations else []
            ),
        }
        return data


class HealthCategory(Base):
    __tablename__ = "health_category"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String)


class HealthTheme(Base):
    __tablename__ = "health_theme"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String)


class DatasetTheme(Base):
    __tablename__ = "dataset_themes"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, ForeignKey("theme.key"))
    value: Mapped[Theme] = relationship(Theme)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="themes")

    def __eq__(self, other):
        if not isinstance(other, DatasetTheme):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetKeyword(Base):
    __tablename__ = "dataset_keywords"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, ForeignKey("keyword.key"))
    value: Mapped[Keyword] = relationship(Keyword)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="keywords")

    def __eq__(self, other):
        if not isinstance(other, DatasetKeyword):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetHealthCategory(Base):
    __tablename__ = "dataset_health_categories"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, ForeignKey("health_category.key"))
    value: Mapped[HealthCategory] = relationship(HealthCategory)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="health_categories"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetHealthCategory):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetHealthTheme(Base):
    __tablename__ = "dataset_health_themes"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, ForeignKey("health_theme.key"))
    value: Mapped[HealthTheme] = relationship(HealthTheme)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="health_themes")

    def __eq__(self, other):
        if not isinstance(other, DatasetHealthTheme):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetTypes(Base):
    __tablename__ = "dataset_types"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, ForeignKey("dataset_type.key"))
    value: Mapped[DatasetType] = relationship(DatasetType)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="dataset_types")

    def __eq__(self, other):
        if not isinstance(other, DatasetType):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetSpatialCoverage(Base):
    __tablename__ = "dataset_spatial_coverages"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, ForeignKey("spatial_coverage.key"))
    value: Mapped[SpatialCoverage] = relationship("SpatialCoverage")
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="spatial_coverages"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetSpatialCoverage):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetConvention(Base):
    __tablename__ = "dataset_conventions"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="conventions")

    def __eq__(self, other):
        if not isinstance(other, DatasetConvention):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetContact(Base):
    __tablename__ = "dataset_contacts"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE")
    )
    contact_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contacts.id", ondelete="CASCADE")
    )

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="contacts")
    contact: Mapped["Contact"] = relationship(
        "Contact", back_populates="dataset_contacts"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetContact):
            return False
        return (
            self.contact_id == other.contact_id and self.dataset_id == other.dataset_id
        )

    def __hash__(self):
        return hash((self.contact_id, self.dataset_id))


class DatasetAreaOfWork(Base):
    __tablename__ = "dataset_area_of_work"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="areas_of_work")

    def __eq__(self, other):
        if not isinstance(other, DatasetAreaOfWork):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetAreaOfCompetence(Base):
    __tablename__ = "dataset_area_of_competence"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="areas_of_competence"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetAreaOfCompetence):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetDataProtectionType(Base):
    __tablename__ = "dataset_data_protection_types"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="data_protection_types"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetDataProtectionType):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetApplicableLegislation(Base):
    __tablename__ = "dataset_applicable_legislation"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    key: Mapped[str] = mapped_column(String, ForeignKey("applicable_legislation.key"))

    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="applicable_legislations"
    )
    applicable_legislation: Mapped[ApplicableLegislation] = relationship(
        "ApplicableLegislation",
        primaryjoin="DatasetApplicableLegislation.key == ApplicableLegislation.key",
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetApplicableLegislation):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class DatasetGroupManagers(Base):
    __tablename__ = "dataset_group_managers"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )

    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="group_managers"
    )
    user: Mapped["User"] = relationship("User", back_populates="dataset_group_managers")

    def __eq__(self, other):
        if not isinstance(other, DatasetGroupManagers):
            return False
        return self.user_id == other.user_id and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.user_id, self.dataset_id))


class DatasetCreator(Base):
    __tablename__ = "dataset_creators"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE")
    )
    organisation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organisations.id")
    )

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="creators")
    organisation: Mapped["Organisation"] = relationship("Organisation")

    def __eq__(self, other):
        if not isinstance(other, DatasetCreator):
            return False
        return (
            self.organisation_id == other.organisation_id
            and self.dataset_id == other.dataset_id
        )

    def __hash__(self):
        return hash((self.organisation_id, self.dataset_id))


class DatasetLanguage(Base):
    __tablename__ = "dataset_languages"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, ForeignKey("language.key"))
    value: Mapped[Language] = relationship(Language)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="languages")

    def __eq__(self, other):
        if not isinstance(other, DatasetLanguage):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class WasGeneratedBy(Base):
    __tablename__ = "dataset_was_generated_by"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, nullable=False)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="was_generated_by"
    )


class DatasetLandingPage(Base):
    __tablename__ = "dataset_landing_pages"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    url: Mapped[str] = mapped_column(String, nullable=False)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE")
    )
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="landing_pages")

    def __eq__(self, other):
        if not isinstance(other, DatasetLandingPage):
            return False
        return self.url == other.url and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.url, self.dataset_id))


class DatasetDocumentation(Base):
    __tablename__ = "dataset_documentation"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    value: Mapped[str] = mapped_column(String, nullable=False)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE")
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="documentation_entries"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetDocumentation):
            return False
        return self.value == other.value and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.value, self.dataset_id))


class DatasetPurpose(Base):
    __tablename__ = "dataset_purpose"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE")
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="purpose_entries"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetPurpose):
            return False
        return self.value == other.value and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.value, self.dataset_id))


class DatasetProvenanceEntry(Base):
    __tablename__ = "dataset_provenance_entries"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE")
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="provenance_entries"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetProvenanceEntry):
            return False
        return self.value == other.value and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.value, self.dataset_id))


class DatasetHealthLegalBasisEntry(Base):
    __tablename__ = "dataset_health_legal_basis_entries"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE")
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="health_legal_basis_entries"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetHealthLegalBasisEntry):
            return False
        return self.value == other.value and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.value, self.dataset_id))


class DatasetVersionNote(Base):
    __tablename__ = "dataset_version_notes"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE")
    )
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="version_notes")

    def __eq__(self, other):
        if not isinstance(other, DatasetVersionNote):
            return False
        return self.value == other.value and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.value, self.dataset_id))


class OtherIdentifier(Base):
    __tablename__ = "dataset_other_identifier"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, nullable=False)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="other_identifiers"
    )


class DatasetConformsTo(Base):
    __tablename__ = "dataset_conforms_to"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, nullable=False)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="conforms_to_values"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetConformsTo):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class SeriesMembership(Base):
    __tablename__ = "series_memberships"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    series_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE"), nullable=False
    )
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    is_first: Mapped[bool] = mapped_column(Boolean, default=False)
    is_last: Mapped[bool] = mapped_column(Boolean, default=False)

    series: Mapped["Dataset"] = relationship(
        "Dataset", foreign_keys=[series_id], back_populates="member_datasets"
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", foreign_keys=[dataset_id], back_populates="series_memberships"
    )

    def __eq__(self, other):
        if not isinstance(other, SeriesMembership):
            return False
        return self.series_id == other.series_id and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.series_id, self.dataset_id))


class DatasetSpatialResolution(Base):
    __tablename__ = "dataset_spatial_resolution"

    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dataset.id"), primary_key=True
    )
    value: Mapped[int] = mapped_column(Integer, primary_key=True)

    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="spatial_resolutions"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetSpatialResolution):
            return False
        return self.dataset_id == other.dataset_id and self.value == other.value

    def __hash__(self):
        return hash((self.dataset_id, self.value))


class DatasetCodingSystem(Base):
    __tablename__ = "dataset_coding_systems"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    value: Mapped[str] = mapped_column(String)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="coding_systems"
    )

    def __eq__(self, other):
        if not isinstance(other, DatasetCodingSystem):
            return False
        return self.dataset_id == other.dataset_id and self.value == other.value

    def __hash__(self):
        return hash((self.dataset_id, self.value))


class DatasetCodeValue(Base):
    __tablename__ = "dataset_code_values"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    value: Mapped[str] = mapped_column(String)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="code_values")

    def __eq__(self, other):
        if not isinstance(other, DatasetCodeValue):
            return False
        return self.dataset_id == other.dataset_id and self.value == other.value

    def __hash__(self):
        return hash((self.dataset_id, self.value))


class DatasetPersonalData(Base):
    __tablename__ = "dataset_personal_data"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="personal_data")

    def __eq__(self, other):
        if not isinstance(other, DatasetPersonalData):
            return False
        return self.key == other.key and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.key, self.dataset_id))


class Dataset(Base):
    __tablename__ = "dataset"
    __table_args__ = (
        Index("ix_dataset_source_lookup", "source", "source_dataset_id"),
        UniqueConstraint("source", "source_dataset_id", name="uq_dataset_source"),
    )

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    authentic_source_reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    release_date: Mapped[date] = mapped_column(Date, nullable=True)
    modified_at: Mapped[date] = mapped_column(Date, nullable=True)
    deprecated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    released_at: Mapped[date] = mapped_column(DateTime(timezone=True), nullable=True)

    previous_version_dataset_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("dataset.id"), nullable=True
    )
    previous_version: Mapped["Dataset"] = relationship(
        "Dataset", remote_side="Dataset.id", backref="next_versions"
    )
    versions: Mapped[List["Dataset"]] = relationship(
        "Dataset",
        back_populates="previous_version",
        cascade="all, delete-orphan",
        overlaps="next_versions",
    )
    time_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    time_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    retention_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    retention_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    rights_statement: Mapped[str] = mapped_column(String)
    periodicity: Mapped[str | None] = mapped_column(
        String, ForeignKey("periodicity.key"), nullable=True
    )
    periodicity_value: Mapped[Periodicity | None] = relationship(Periodicity)
    status: Mapped[str] = mapped_column(String, default=DatasetStatus.DRAFT.value)
    version: Mapped[str] = mapped_column(String)
    version_change_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    version_notes: Mapped[List[DatasetVersionNote]] = relationship(
        "DatasetVersionNote",
        order_by="DatasetVersionNote.id",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    duration_of_administrative_utility: Mapped[int] = mapped_column(Integer)
    max_typical_age: Mapped[int] = mapped_column(Integer, nullable=True)
    min_typical_age: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_records: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_unique_individuals: Mapped[int] = mapped_column(Integer, nullable=True)
    final_disposition: Mapped[str] = mapped_column(String)
    identifier: Mapped[str] = mapped_column(String(36), nullable=False)
    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Source instance identifier (e.g., 'instance-1')",
    )
    source_dataset_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Dataset ID in the source instance"
    )
    monitoring_location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    publisher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organisations.id"), nullable=True
    )
    publisher: Mapped[Organisation] = relationship(
        "Organisation", foreign_keys=[publisher_id]
    )
    user: Mapped[User] = relationship("User", foreign_keys=[user_id])

    dataset_types: Mapped[Set[DatasetTypes]] = relationship(
        "DatasetTypes",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    themes: Mapped[Set[DatasetTheme]] = relationship(
        "DatasetTheme",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    qualified_attributions: Mapped[Set["DatasetQualifiedAttribution"]] = relationship(
        "DatasetQualifiedAttribution",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    keywords: Mapped[Set[DatasetKeyword]] = relationship(
        "DatasetKeyword",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    health_categories: Mapped[Set[DatasetHealthCategory]] = relationship(
        "DatasetHealthCategory",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    health_themes: Mapped[Set[DatasetHealthTheme]] = relationship(
        "DatasetHealthTheme",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    spatial_coverages: Mapped[Set[DatasetSpatialCoverage]] = relationship(
        "DatasetSpatialCoverage",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    conventions: Mapped[Set[DatasetConvention]] = relationship(
        "DatasetConvention",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    areas_of_work: Mapped[Set[DatasetAreaOfWork]] = relationship(
        "DatasetAreaOfWork",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    areas_of_competence: Mapped[Set[DatasetAreaOfCompetence]] = relationship(
        "DatasetAreaOfCompetence",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    applicable_legislations: Mapped[Set[DatasetApplicableLegislation]] = relationship(
        "DatasetApplicableLegislation",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    notes: Mapped[str] = mapped_column(String)
    dataset_comments: Mapped[Set[DatasetComment]] = relationship(
        "DatasetComment",
        foreign_keys=[DatasetComment.dataset_id],
        collection_class=set,
        cascade="all, delete-orphan",
    )
    distributions: Mapped[Set[Distribution]] = relationship(
        "Distribution",
        foreign_keys=[Distribution.dataset_id],
        collection_class=set,
        cascade="all, delete-orphan",
    )
    data_dictionaries: Mapped[Set[DataDictionaryEntry]] = relationship(
        "DataDictionaryEntry",
        foreign_keys=[DataDictionaryEntry.dataset_id],
        collection_class=set,
        cascade="all, delete-orphan",
    )
    source_relations: Mapped[Set[DatasetRelation]] = relationship(
        "DatasetRelation",
        foreign_keys=[DatasetRelation.source_dataset],
        collection_class=set,
        cascade="all, delete-orphan",
    )
    target_relations: Mapped[Set[DatasetRelation]] = relationship(
        "DatasetRelation",
        foreign_keys=[DatasetRelation.target_dataset],
        collection_class=set,
        cascade="all, delete-orphan",
    )
    group_managers: Mapped[Set[DatasetGroupManagers]] = relationship(
        "DatasetGroupManagers",
        foreign_keys=[DatasetGroupManagers.dataset_id],
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    creators: Mapped[Set[DatasetCreator]] = relationship(
        "DatasetCreator",
        foreign_keys=[DatasetCreator.dataset_id],
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    contacts: Mapped[Set[DatasetContact]] = relationship(
        "DatasetContact",
        foreign_keys=[DatasetContact.dataset_id],
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    data_protection_types: Mapped[Set[DatasetDataProtectionType]] = relationship(
        "DatasetDataProtectionType",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    provenance_entries: Mapped[List[DatasetProvenanceEntry]] = relationship(
        "DatasetProvenanceEntry",
        order_by="DatasetProvenanceEntry.id",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    health_legal_basis_entries: Mapped[List[DatasetHealthLegalBasisEntry]] = (
        relationship(
            "DatasetHealthLegalBasisEntry",
            collection_class=list,
            back_populates="dataset",
            cascade="all, delete-orphan",
        )
    )
    languages: Mapped[Set[DatasetLanguage]] = relationship(
        "DatasetLanguage",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    landing_pages: Mapped[List[DatasetLandingPage]] = relationship(
        "DatasetLandingPage",
        order_by="DatasetLandingPage.id",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    documentation_entries: Mapped[List[DatasetDocumentation]] = relationship(
        "DatasetDocumentation",
        order_by="DatasetDocumentation.id",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    purpose_entries: Mapped[Set[DatasetPurpose]] = relationship(
        "DatasetPurpose",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    is_dataset_series: Mapped[bool] = mapped_column(Boolean, default=False)
    member_datasets: Mapped[Set[SeriesMembership]] = relationship(
        "SeriesMembership",
        foreign_keys=[SeriesMembership.series_id],
        back_populates="series",
        collection_class=set,
        cascade="all, delete-orphan",
    )
    series_memberships: Mapped[Set[SeriesMembership]] = relationship(
        "SeriesMembership",
        foreign_keys=[SeriesMembership.dataset_id],
        back_populates="dataset",
        collection_class=set,
        cascade="all, delete-orphan",
    )
    was_generated_by: Mapped[Set[WasGeneratedBy]] = relationship(
        "WasGeneratedBy",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    other_identifiers: Mapped[Set[OtherIdentifier]] = relationship(
        "OtherIdentifier",
        collection_class=set,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    conforms_to_values: Mapped[List[DatasetConformsTo]] = relationship(
        "DatasetConformsTo",
        order_by="DatasetConformsTo.id",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    spatial_resolutions: Mapped[List[DatasetSpatialResolution]] = relationship(
        "DatasetSpatialResolution",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    personal_data: Mapped[List[DatasetPersonalData]] = relationship(
        "DatasetPersonalData",
        collection_class=list,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    temporal_resolution: Mapped[str] = mapped_column(String)
    population_coverage: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    code_values: Mapped[List[DatasetCodeValue]] = relationship(
        "DatasetCodeValue",
        collection_class=list,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    coding_systems: Mapped[List[DatasetCodingSystem]] = relationship(
        "DatasetCodingSystem",
        collection_class=list,
        back_populates="dataset",
        cascade="all, delete-orphan",
    )

    @property
    def monitoring_location_or_legacy(self) -> Optional[str]:
        return self.monitoring_location

    def __eq__(self, other):
        if not isinstance(other, Dataset):
            return False
        return self.title == other.title

    def __hash__(self):
        return hash((self.title))

    def to_dict_for_diff(self):
        data = {
            "title": self.title,
            "description": self.description,
            "contact_ids": (
                [dc.contact_id for dc in self.contacts] if self.contacts else []
            ),
            "time_period_start": (
                self.time_period_start.isoformat() if self.time_period_start else None
            ),
            "time_period_end": (
                self.time_period_end.isoformat() if self.time_period_end else None
            ),
            "retention_period_start": (
                self.retention_period_start.isoformat()
                if self.retention_period_start
                else None
            ),
            "retention_period_end": (
                self.retention_period_end.isoformat()
                if self.retention_period_end
                else None
            ),
            "rights_statement": self.rights_statement,
            "periodicity": self.periodicity,
            "status": self.status,
            "notes": self.notes,
            "release_date": (
                self.release_date.isoformat() if self.release_date else None
            ),
            "released_at": (self.released_at.isoformat() if self.released_at else None),
            "modified_at": (self.modified_at.isoformat() if self.modified_at else None),
            "deprecated_at": (
                self.deprecated_at.isoformat() if self.deprecated_at else None
            ),
            "version": self.version,
            "version_notes": (
                [vn.value for vn in self.version_notes]
                if self.version_notes is not None
                else []
            ),
            "duration_of_administrative_utility": self.duration_of_administrative_utility,
            "max_typical_age": self.max_typical_age,
            "min_typical_age": self.min_typical_age,
            "number_of_records": self.number_of_records,
            "number_of_unique_individuals": self.number_of_unique_individuals,
            "final_disposition": self.final_disposition,
            "spatial_resolutions": (
                [sr.value for sr in self.spatial_resolutions]
                if self.spatial_resolutions
                else []
            ),
            "temporal_resolution": self.temporal_resolution,
            "dataset_types": (
                [dataset_type.key for dataset_type in self.dataset_types]
                if self.dataset_types
                else []
            ),
            "themes": [theme.key for theme in self.themes] if self.themes else [],
            "keywords": (
                [keyword.key for keyword in self.keywords] if self.keywords else []
            ),
            "health_categories": (
                [hc.key for hc in self.health_categories]
                if self.health_categories
                else []
            ),
            "health_themes": (
                [ht.key for ht in self.health_themes] if self.health_themes else []
            ),
            "spatial_coverages": (
                [spatial_coverage.key for spatial_coverage in self.spatial_coverages]
                if self.spatial_coverages
                else []
            ),
            "conventions": (
                [convention.key for convention in self.conventions]
                if self.conventions
                else []
            ),
            "areas_of_work": (
                [aow.key for aow in self.areas_of_work] if self.areas_of_work else []
            ),
            "areas_of_competence": (
                [aoc.key for aoc in self.areas_of_competence]
                if self.areas_of_competence is not None
                else []
            ),
            "applicable_legislations": (
                [al.key for al in self.applicable_legislations]
                if self.applicable_legislations is not None
                else []
            ),
            "publisher_id": self.publisher_id,
            "creator_ids": (
                [creator.organisation_id for creator in self.creators]
                if self.creators is not None
                else []
            ),
            "group_managers": (
                [group_manager.user.id for group_manager in self.group_managers]
                if self.group_managers is not None
                else []
            ),
            "monitoring_location": self.monitoring_location,
            "data_protection_types": (
                [dpt.key for dpt in self.data_protection_types]
                if self.data_protection_types is not None
                else []
            ),
            "provenance": (
                [p.value for p in self.provenance_entries]
                if self.provenance_entries is not None
                else []
            ),
            "health_legal_basis": (
                [hlb.value for hlb in self.health_legal_basis_entries]
                if self.health_legal_basis_entries is not None
                else []
            ),
            "languages": (
                [language.key for language in self.languages]
                if self.languages is not None
                else []
            ),
            "landing_pages": (
                [landing_page.url for landing_page in self.landing_pages]
                if self.landing_pages is not None
                else []
            ),
            "documentation": (
                [doc.value for doc in self.documentation_entries]
                if self.documentation_entries is not None
                else []
            ),
            "purpose": (
                [purpose.value for purpose in self.purpose_entries]
                if self.purpose_entries is not None
                else []
            ),
            "conforms_to": (
                [ct.key for ct in self.conforms_to_values]
                if self.conforms_to_values is not None
                else []
            ),
            "is_dataset_series": self.is_dataset_series,
            "member_datasets": (
                [member_dataset.dataset_id for member_dataset in self.member_datasets]
                if self.member_datasets is not None
                else []
            ),
            "was_generated_by": (
                [id.key for id in self.was_generated_by]
                if self.was_generated_by is not None
                else []
            ),
            "other_identifiers": (
                [id.key for id in self.other_identifiers]
                if self.other_identifiers is not None
                else []
            ),
            "personal_data": (
                [pd.key for pd in self.personal_data]
                if self.personal_data is not None
                else []
            ),
            "population_coverage": self.population_coverage,
            "code_values": (
                [cv.value for cv in self.code_values]
                if self.code_values is not None
                else []
            ),
            "coding_systems": (
                [cs.value for cs in self.coding_systems]
                if self.coding_systems is not None
                else []
            ),
        }

        return data
