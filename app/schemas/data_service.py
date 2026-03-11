from pydantic import BaseModel, Field
from typing import List, Annotated
from models.data_service import DataService
from typing import List, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class DataServiceEndpointDto(BaseModel):
    endpoint_url: Annotated[
        str,
        Field(
            min_length=1, max_length=500, description="Endpoint URL (1-500 characters)"
        ),
    ]
    endpoint_description: Optional[
        Annotated[
            str,
            Field(
                max_length=1000,
                description="Endpoint description (max 1000 characters)",
            ),
        ]
    ] = None

    class Config:
        extra = "forbid"
        str_strip_whitespace = True


@dataclass(frozen=True)
class DataServiceDto(BaseModel):
    title: Annotated[
        str,
        Field(
            min_length=1, max_length=200, description="Service title (1-200 characters)"
        ),
    ]
    endpoints: Annotated[
        List[DataServiceEndpointDto],
        Field(max_length=50, description="Service endpoints (max 50 endpoints)"),
    ] = Field(default_factory=list)

    class Config:
        orm_mode = True
        extra = "forbid"
        str_strip_whitespace = True


@dataclass(frozen=True)
class ResourceDataService(BaseModel):
    id: int
    title: str
    endpoints: frozenset[DataServiceEndpointDto]

    class Config:
        orm_mode = True


def data_service_entity_to_resource(data_service: DataService) -> ResourceDataService:
    return ResourceDataService(
        id=data_service.id,
        title=data_service.title,
        endpoints=frozenset(
            [
                DataServiceEndpointDto(
                    endpoint_url=endpoint.endpoint_url,
                    endpoint_description=endpoint.endpoint_description,
                )
                for endpoint in data_service.endpoints
            ]
        ),
    )
