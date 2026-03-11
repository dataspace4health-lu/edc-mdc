from fastapi import Depends, HTTPException
from schemas.data_service import (
    DataServiceDto,
    ResourceDataService,
    data_service_entity_to_resource,
)
from models.data_service import DataService, DataServiceEndpoint
from repositories.data_service import DataServiceRepository
from typing import List


class DataServiceService:
    def __init__(
        self,
        data_service_repository: DataServiceRepository = Depends(DataServiceRepository),
    ):
        self._data_service_repository = data_service_repository

    def get_data_services(self) -> List[ResourceDataService]:
        return [
            data_service_entity_to_resource(data_service)
            for data_service in self._data_service_repository.get_data_services()
        ]

    def get_data_service(self, data_service_id: int) -> ResourceDataService:
        data_service = self._data_service_repository.get_data_service(data_service_id)
        return data_service_entity_to_resource(data_service)

    def create_data_service(
        self, data_service_dto: DataServiceDto
    ) -> ResourceDataService:
        if (
            self._data_service_repository.get_by_title(data_service_dto.title)
            is not None
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Data Service with title '{data_service_dto.title}' already exists.",
            )

        if len(data_service_dto.endpoints) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Data Service must have at least one endpoint.",
            )

        endpoints = [
            DataServiceEndpoint(
                endpoint_url=endpoint.endpoint_url,
                endpoint_description=endpoint.endpoint_description,
            )
            for endpoint in data_service_dto.endpoints
        ]

        data_service = DataService(
            title=data_service_dto.title,
            endpoints=endpoints,
        )
        self._data_service_repository.add(data_service)
        self._data_service_repository.commit()
        self._data_service_repository.refresh(data_service)

        return data_service_entity_to_resource(data_service)

    def update_data_service(
        self,
        data_service_id: int,
        data_service_dto: DataServiceDto,
    ) -> ResourceDataService:
        data_service = self._data_service_repository.get_data_service(data_service_id)
        if not data_service:
            raise HTTPException(
                status_code=404, detail=f"Data Service[{data_service_id}] not found."
            )

        same_titled = self._data_service_repository.get_by_title(data_service_dto.title)
        if same_titled is not None and same_titled.id is not data_service.id:
            raise HTTPException(
                status_code=400,
                detail=f"Data Service with title '{data_service_dto.title}' already exists.",
            )

        if len(data_service_dto.endpoints) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Data Service must have at least one endpoint.",
            )

        data_service.title = data_service_dto.title
        data_service.endpoints.clear()

        for endpoint in data_service_dto.endpoints:
            data_service.endpoints.append(
                DataServiceEndpoint(
                    endpoint_url=endpoint.endpoint_url,
                    endpoint_description=endpoint.endpoint_description,
                )
            )

        self._data_service_repository.commit()
        self._data_service_repository.refresh(data_service)

        return data_service_entity_to_resource(data_service)
