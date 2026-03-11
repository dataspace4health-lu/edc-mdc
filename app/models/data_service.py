from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from dependencies.database import Base
from typing import List


class DataServiceEndpoint(Base):
    __tablename__ = "data_service_endpoint"
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    endpoint_url: Mapped[str] = mapped_column(String, nullable=False)
    endpoint_description: Mapped[str] = mapped_column(String, nullable=True)
    data_service_id: Mapped[int] = mapped_column(Integer, ForeignKey("data_service.id"))
    data_service: Mapped["DataService"] = relationship(
        "DataService", back_populates="endpoints"
    )

    def to_dict(self):
        return {"url": self.endpoint_url, "description": self.endpoint_description}


class DataService(Base):
    __tablename__ = "data_service"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    endpoints: Mapped[List[DataServiceEndpoint]] = relationship(
        "DataServiceEndpoint",
        back_populates="data_service",
        cascade="all, delete-orphan",
    )

    def __eq__(self, other):
        if not isinstance(other, DataService):
            return False
        if len(self.endpoints) != len(other.endpoints):
            return False

        self_endpoints = sorted(self.endpoints, key=lambda x: x.endpoint_url)
        other_endpoints = sorted(other.endpoints, key=lambda x: x.endpoint_url)
        return all(
            self_endpoint.endpoint_url == other_endpoint.endpoint_url
            and self_endpoint.endpoint_description
            == other_endpoint.endpoint_description
            for self_endpoint, other_endpoint in zip(self_endpoints, other_endpoints)
        )

    def __hash__(self):
        return hash((self.title, self.id))

    def to_dict_for_diff(self):
        return {
            "title": self.title,
            "endpoints": (
                [endpoint.to_dict() for endpoint in self.endpoints]
                if self.endpoints
                else []
            ),
        }
