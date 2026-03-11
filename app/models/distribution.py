from datetime import date
from enum import Enum
from typing import List, Set

from dependencies.database import Base
from models.language import Language
from models.data_service import DataService
from models.applicable_legislation import ApplicableLegislation
from models.spatial_coverage import SpatialCoverage
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PolicyType(str, Enum):
    SET = "odrl:Set"
    OFFER = "odrl:Offer"


class DistributionDcatStatus(str, Enum):
    COMPLETED = "Completed"
    DEPRECATED = "Deprecated"
    UNDER_DEVELOPMENT = "Under Development"
    WITHDRAWN = "Withdrawn"


class ActionType(str, Enum):
    PERMISSION = "permission"
    PROHIBITION = "prohibition"


class ConstraintType(str, Enum):
    PURPOSE = "purpose"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    INDUSTRY = "industry"


class FileType(Base):
    __tablename__ = "file_type"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String)


class License(Base):
    __tablename__ = "license"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String)


class LinkedSchema(Base):
    __tablename__ = "distribution_linked_schema"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, nullable=False)
    distribution_id: Mapped[int] = mapped_column(Integer, ForeignKey("distribution.id"))
    distribution: Mapped["Distribution"] = relationship(
        "Distribution", back_populates="linked_schemas"
    )


class DistributionDocumentation(Base):
    __tablename__ = "distribution_documentation"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    value: Mapped[str] = mapped_column(String, nullable=False)
    distribution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("distribution.id", ondelete="CASCADE")
    )
    distribution: Mapped["Distribution"] = relationship(
        "Distribution", back_populates="documentation_entries"
    )

    def __eq__(self, other):
        if not isinstance(other, DistributionDocumentation):
            return False
        return (
            self.value == other.value and self.distribution_id == other.distribution_id
        )

    def __hash__(self):
        return hash((self.value, self.distribution_id))


class DistributionLanguage(Base):
    __tablename__ = "distribution_languages"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, ForeignKey("language.key"))
    value: Mapped[Language] = relationship(Language)
    distribution_id: Mapped[int] = mapped_column(Integer, ForeignKey("distribution.id"))
    distribution: Mapped["Distribution"] = relationship(
        "Distribution", back_populates="languages"
    )

    def __eq__(self, other):
        if not isinstance(other, DistributionLanguage):
            return False
        return self.key == other.key and self.distribution_id == other.distribution_id

    def __hash__(self):
        return hash((self.key, self.distribution_id))


class DistributionAccessService(Base):
    __tablename__ = "distribution_access_service"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    distribution_id: Mapped[int] = mapped_column(Integer, ForeignKey("distribution.id"))
    distribution: Mapped["Distribution"] = relationship(
        "Distribution", back_populates="access_services"
    )
    data_service_id: Mapped[int] = mapped_column(Integer, ForeignKey("data_service.id"))
    data_service: Mapped["DataService"] = relationship("DataService")


class DistributionApplicableLegislation(Base):
    __tablename__ = "distribution_applicable_legislation"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    distribution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("distribution.id"), nullable=False
    )
    key: Mapped[str] = mapped_column(String, ForeignKey("applicable_legislation.key"))

    distribution: Mapped["Distribution"] = relationship(
        "Distribution", back_populates="applicable_legislations"
    )
    applicable_legislation: Mapped["ApplicableLegislation"] = relationship(
        "ApplicableLegislation",
        primaryjoin="DistributionApplicableLegislation.key == ApplicableLegislation.key",
    )

    def __eq__(self, other):
        if not isinstance(other, DistributionApplicableLegislation):
            return False
        return self.key == other.key and self.distribution_id == other.distribution_id

    def __hash__(self):
        return hash((self.key, self.distribution_id))


class DistributionSpatialRestrictions(Base):
    __tablename__ = "distribution_spatial_restrictions"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    key: Mapped[str] = mapped_column(String, ForeignKey("spatial_coverage.key"))
    value: Mapped[SpatialCoverage] = relationship("SpatialCoverage")

    policy_action_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("distribution_policy_actions.id"), nullable=False
    )
    policy_action: Mapped["DistributionPolicyAction"] = relationship(
        "DistributionPolicyAction", back_populates="spatial_restrictions"
    )

    def __eq__(self, other):
        return (
            isinstance(other, DistributionSpatialRestrictions)
            and self.policy_action_id == other.policy_action_id
            and self.key == other.key
        )

    def __hash__(self):
        return hash((self.policy_action_id, self.key))


class DistributionPolicyAction(Base):
    __tablename__ = "distribution_policy_actions"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    distribution_id: Mapped[int] = mapped_column(Integer, ForeignKey("distribution.id"))

    policy_action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    policy_constraint_type: Mapped[str] = mapped_column(String(50), nullable=True)

    policy_constraint_value: Mapped[str] = mapped_column(String(255), nullable=True)
    temporal_restriction_start: Mapped[date] = mapped_column(Date, nullable=True)
    temporal_restriction_end: Mapped[date] = mapped_column(Date, nullable=True)

    distribution: Mapped["Distribution"] = relationship(
        "Distribution", back_populates="policy_actions"
    )
    spatial_restrictions: Mapped[Set["DistributionSpatialRestrictions"]] = relationship(
        "DistributionSpatialRestrictions",
        collection_class=set,
        back_populates="policy_action",
        cascade="all, delete-orphan",
    )

    def __eq__(self, other):
        if not isinstance(other, DistributionPolicyAction):
            return False
        return (
            self.distribution_id == other.distribution_id
            and self.policy_action_type == other.policy_action_type
            and self.policy_constraint_type == other.policy_constraint_type
            and self.policy_constraint_value == other.policy_constraint_value
            and self.temporal_restriction_start == other.temporal_restriction_start
            and self.temporal_restriction_end == other.temporal_restriction_end
        )

    def __hash__(self):
        return hash(
            (
                self.distribution_id,
                self.policy_action_type,
                self.policy_constraint_type,
                self.policy_constraint_value,
                self.temporal_restriction_start,
                self.temporal_restriction_end,
            )
        )


class DistributionAccessUrl(Base):
    __tablename__ = "distribution_access_urls"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    url: Mapped[str] = mapped_column(String, nullable=False)
    distribution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("distribution.id", ondelete="CASCADE")
    )
    distribution: Mapped["Distribution"] = relationship(
        "Distribution", back_populates="access_urls"
    )

    def __eq__(self, other):
        if not isinstance(other, DistributionAccessUrl):
            return False
        return self.url == other.url and self.distribution_id == other.distribution_id

    def __hash__(self):
        return hash((self.url, self.distribution_id))


class DistributionDownloadUrl(Base):
    __tablename__ = "distribution_download_urls"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    url: Mapped[str] = mapped_column(String, nullable=False)
    distribution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("distribution.id", ondelete="CASCADE")
    )
    distribution: Mapped["Distribution"] = relationship(
        "Distribution", back_populates="download_urls"
    )

    def __eq__(self, other):
        if not isinstance(other, DistributionDownloadUrl):
            return False
        return self.url == other.url and self.distribution_id == other.distribution_id

    def __hash__(self):
        return hash((self.url, self.distribution_id))


class Distribution(Base):
    __tablename__ = "distribution"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset.id"))
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", foreign_keys=[dataset_id], back_populates="distributions"
    )
    download_urls: Mapped[List[DistributionDownloadUrl]] = relationship(
        "DistributionDownloadUrl",
        back_populates="distribution",
        cascade="all, delete-orphan",
    )
    access_urls: Mapped[List[DistributionAccessUrl]] = relationship(
        "DistributionAccessUrl",
        back_populates="distribution",
        cascade="all, delete-orphan",
    )
    file_type: Mapped[str] = mapped_column(String, ForeignKey("file_type.key"))
    file_type_value: Mapped[FileType] = relationship(FileType)
    rights_statement: Mapped[str] = mapped_column(String)
    internal_only: Mapped[bool] = mapped_column(Boolean)
    is_analytics: Mapped[bool] = mapped_column(Boolean, default=False)
    applicable_legislations: Mapped[Set[DistributionApplicableLegislation]] = (
        relationship(
            "DistributionApplicableLegislation",
            collection_class=set,
            back_populates="distribution",
            cascade="all, delete-orphan",
        )
    )
    languages: Mapped[Set[DistributionLanguage]] = relationship(
        "DistributionLanguage",
        collection_class=set,
        back_populates="distribution",
        cascade="all, delete-orphan",
    )
    notes: Mapped[str] = mapped_column(String)
    license: Mapped[str] = mapped_column(
        String, ForeignKey("license.key"), nullable=True
    )
    license_value: Mapped["License"] = relationship("License")
    distribution_path: Mapped[str] = mapped_column(String(100), nullable=True)
    availability: Mapped[str] = mapped_column(String(100), nullable=True)
    documentation_entries: Mapped[List["DistributionDocumentation"]] = relationship(
        "DistributionDocumentation",
        back_populates="distribution",
        cascade="all, delete-orphan",
    )
    byte_size: Mapped[int] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str] = mapped_column(String, nullable=True)
    modification_date: Mapped[date] = mapped_column(Date, nullable=True)
    release_date: Mapped[date] = mapped_column(Date, nullable=True)
    linked_schemas: Mapped[List[LinkedSchema]] = relationship(
        "LinkedSchema",
        back_populates="distribution",
        cascade="all, delete-orphan",
    )
    policy_type: Mapped[str] = mapped_column(SQLAlchemyEnum(PolicyType), nullable=True)
    policy_actions: Mapped[Set[DistributionPolicyAction]] = relationship(
        "DistributionPolicyAction",
        collection_class=set,
        back_populates="distribution",
        cascade="all, delete-orphan",
    )
    media_type: Mapped[str] = mapped_column(String, nullable=True)
    compression_format: Mapped[str] = mapped_column(String, nullable=True)
    packaging_format: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[date] = mapped_column(DateTime)
    distribution_dcat_status: Mapped[str] = mapped_column(
        SQLAlchemyEnum(DistributionDcatStatus), nullable=True
    )
    spatial_resolution: Mapped[int] = mapped_column(Integer, nullable=True)
    temporal_resolution: Mapped[str] = mapped_column(String, nullable=True)
    access_services: Mapped[Set[DistributionAccessService]] = relationship(
        "DistributionAccessService",
        collection_class=set,
        back_populates="distribution",
        cascade="all, delete-orphan",
    )

    def __eq__(self, other):
        if not isinstance(other, Distribution):
            return False
        return self.title == other.title and self.dataset_id == other.dataset_id

    def __hash__(self):
        return hash((self.title, self.dataset_id))

    def to_dict_for_diff(self) -> dict:
        data = {
            "title": self.title,
            "description": self.description,
            "download_urls": (
                [download_urls.url for download_urls in self.download_urls]
                if self.download_urls is not None
                else []
            ),
            "access_urls": (
                [access_url.url for access_url in self.access_urls]
                if self.access_urls is not None
                else []
            ),
            "file_type": self.file_type,
            "rights_statement": self.rights_statement,
            "languages": (
                [language.key for language in self.languages]
                if self.languages is not None
                else []
            ),
            "internal_only": self.internal_only,
            # Normalize None to False for is_analytics to prevent false positive diffs
            # Old distributions created before migration a3d3828a3351 have NULL values
            "is_analytics": (
                self.is_analytics if self.is_analytics is not None else False
            ),
            "applicable_legislations": (
                [
                    applicable_legislation.key
                    for applicable_legislation in self.applicable_legislations
                ]
                if self.applicable_legislations is not None
                else []
            ),
            "notes": self.notes,
            "license": self.license,
            "distribution_path": self.distribution_path,
            "availability": self.availability,
            "documentation": (
                [doc.value for doc in self.documentation_entries]
                if self.documentation_entries is not None
                else []
            ),
            "modification_date": (
                self.modification_date.isoformat() if self.modification_date else None
            ),
            "release_date": (
                self.release_date.isoformat() if self.release_date else None
            ),
            "linked_schemas": (
                [schema.key for schema in self.linked_schemas]
                if self.linked_schemas is not None
                else []
            ),
            "media_type": self.media_type,
            "compression_format": self.compression_format,
            "packaging_format": self.packaging_format,
            "distribution_dcat_status": (
                self.distribution_dcat_status.value
                if self.distribution_dcat_status is not None
                else None
            ),
            "spatial_resolution": self.spatial_resolution,
            "temporal_resolution": self.temporal_resolution,
            "access_service_ids": (
                [service.data_service.id for service in self.access_services]
                if self.access_services is not None
                else []
            ),
        }

        data["policy_actions"] = []
        if self.policy_actions:
            for policy_action in self.policy_actions:
                data["policy_actions"].append(
                    {
                        "policy_action_type": policy_action.policy_action_type,
                        "policy_constraint_type": policy_action.policy_constraint_type,
                        "policy_constraint_value": policy_action.policy_constraint_value,
                        "temporal_restriction_start": (
                            policy_action.temporal_restriction_start.isoformat()
                            if policy_action.temporal_restriction_start
                            else None
                        ),
                        "temporal_restriction_end": (
                            policy_action.temporal_restriction_end.isoformat()
                            if policy_action.temporal_restriction_end
                            else None
                        ),
                        "spatial_restrictions": (
                            [
                                restriction.key
                                for restriction in policy_action.spatial_restrictions
                            ]
                            if policy_action.spatial_restrictions
                            else []
                        ),
                    }
                )

        return data
