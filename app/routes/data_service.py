from fastapi import Depends, status, APIRouter
from schemas.data_service import (
    DataServiceDto,
    ResourceDataService,
)
from services.data_service import DataServiceService
from typing import List, Annotated
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context

router = APIRouter()


@router.get(
    "/api/v1/data_services",
    response_model=List[ResourceDataService],
    tags=["data_services"],
)
def get_data_services(
    service: Annotated[DataServiceService, Depends(DataServiceService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["form-fields:edit", "form-fields:edit:my", "form-fields:edit:organisation"]
        )
    ),
) -> List[ResourceDataService]:
    return service.get_data_services()


@router.get(
    "/api/v1/data_services/{data_service_id}",
    response_model=ResourceDataService,
    tags=["data_services"],
)
def get_data_service_by_id(
    data_service_id: int,
    service: Annotated[DataServiceService, Depends(DataServiceService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["form-fields:edit", "form-fields:edit:my", "form-fields:edit:organisation"]
        )
    ),
) -> ResourceDataService:
    return service.get_data_service(data_service_id)


@router.post(
    "/api/v1/data_services",
    response_model=ResourceDataService,
    tags=["data_services"],
    status_code=status.HTTP_201_CREATED,
)
def create_data_service(
    data_service_dto: DataServiceDto,
    service: Annotated[DataServiceService, Depends(DataServiceService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["form-fields:edit", "form-fields:edit:my", "form-fields:edit:organisation"]
        )
    ),
) -> ResourceDataService:
    return service.create_data_service(data_service_dto)


@router.put(
    "/api/v1/data_services/{data_service_id}",
    response_model=ResourceDataService,
    tags=["data_services"],
)
def update_data_service(
    data_service_id: int,
    data_service_dto: DataServiceDto,
    service: Annotated[DataServiceService, Depends(DataServiceService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["form-fields:edit", "form-fields:edit:my", "form-fields:edit:organisation"]
        )
    ),
) -> ResourceDataService:
    return service.update_data_service(data_service_id, data_service_dto)
