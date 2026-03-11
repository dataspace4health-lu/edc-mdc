from typing import Annotated, List, Optional

from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from schemas.distribution import PolicyActionDto
from services.distribution import DistributionService
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Body,
)
from fastapi.responses import Response
from models.identity_context import IdentityContext
from models.dataset import DatasetVersionChangeType
from repositories.dataset import DatasetRepository
from repositories.organisation import OrganisationRepository
from routes.auth import validate_and_retrieve_identity_context
from schemas.dataset import (
    DatasetDto,
    DatasetListRequest,
    DatasetStatusUpdateDto,
    DatasetVersionCreateDto,
    PaginatedDatasetResponse,
    DatasetCountsResponse,
    ResourceDataset,
    dataset_entity_to_resource,
)
from schemas.dataset_comment import DatasetCommentDto
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.database_session_manager import DatabaseSessionManager
from services.dataset import DatasetService
from services.catalogues.importers.dataset_rdf_import_service import (
    DatasetRDFImportService,
)
from services.lnds_hosted_dataset_import_factory import (
    create_dataset_rdf_import_service_from_dependencies,
)
from services.dataset_comment import DatasetCommentService
from services.dataset_status import DatasetStatusService
from services.dataset_permissions_service import DatasetPermissionsService
from services.email_service import EmailService
from services.emails.dataset_versioning_email import DatasetVersioningEmailService
from services.catalogue import CatalogueService
from services.config import ConfigService, get_config_service
from schemas.catalogue import CatalogueFormat
from fastapi.responses import JSONResponse
from utils.error_responses import ErrorResponse

router = APIRouter()


def get_dataset_rdf_import_service(
    db_session: Annotated[Session, Depends(get_db_session)],
) -> DatasetRDFImportService:
    return create_dataset_rdf_import_service_from_dependencies(db_session)


def get_status_service(
    dataset_id: int,
    dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)],
    database_session_manager: Annotated[
        DatabaseSessionManager, Depends(DatabaseSessionManager)
    ],
    email_service: Annotated[EmailService, Depends(EmailService)],
    dataset_versioning_email_service: Annotated[
        DatasetVersioningEmailService, Depends(DatasetVersioningEmailService)
    ],
    activity_log_service: Annotated[
        DatasetActivityLogService, Depends(DatasetActivityLogService)
    ],
    config_service: Annotated[ConfigService, Depends(get_config_service)],
    dataset_permissions_service: Annotated[
        DatasetPermissionsService, Depends(DatasetPermissionsService)
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:status-change:complete",
                "datasets:status-change:complete:my",
                "datasets:status-change:complete:group",
                "datasets:status-change:complete:organisation",
                "datasets:status-change:draft",
                "datasets:status-change:validate",
                "datasets:status-change:approve",
                "datasets:status-change:publish",
                "datasets:status-change:internal-only",
                "datasets:status-change:deprecate",
            ]
        )
    ),
) -> DatasetStatusService:
    return DatasetStatusService(
        dataset_id=dataset_id,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        identity=identity,
        email_service=email_service,
        activity_log_service=activity_log_service,
        dataset_versioning_email_service=dataset_versioning_email_service,
        config_service=config_service,
        dataset_permissions_service=dataset_permissions_service,
    )


@router.post(
    "/api/v1/paginated_datasets",
    response_model=PaginatedDatasetResponse,
    tags=["dataset"],
)
def paginated_datasets(
    request: DatasetListRequest,
    service: Annotated[DatasetService, Depends(DatasetService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
                "datasets:read:all-after-draft",
                "datasets:read:all-after-draft:organisation",
                "datasets:read:all-after-complete",
                "datasets:read:completed",
                "datasets:read:validated",
                "datasets:read:approved",
                "datasets:read:published",
            ]
        )
    ),
) -> List[ResourceDataset]:
    return service.get_paginated_datasets(
        identity=identity,
        status=request.status,
        page=request.page,
        page_size=request.page_size,
        query=request.query,
        dataset_types=request.dataset_types,
        rights_statements=request.rights_statements,
        keywords=request.keywords,
        themes=request.themes,
        applicable_legislations=request.applicable_legislations,
        periodicities=request.periodicities,
        organisations=request.organisations,
        authentic_source_pending=request.authentic_source_pending,
        has_unlabeled_authentic_source=request.has_unlabeled_authentic_source,
    )


@router.get(
    "/api/v1/datasets/counts",
    response_model=DatasetCountsResponse,
    tags=["dataset"],
)
def get_dataset_counts(
    service: Annotated[DatasetService, Depends(DatasetService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
                "datasets:read:all-after-draft",
                "datasets:read:all-after-draft:organisation",
                "datasets:read:all-after-complete",
                "datasets:read:completed",
                "datasets:read:validated",
                "datasets:read:approved",
                "datasets:read:published",
            ]
        )
    ),
) -> DatasetCountsResponse:
    return service.get_dataset_counts(identity)


@router.get(
    "/api/v1/datasets/{dataset_id}",
    response_model=ResourceDataset,
    tags=["dataset"],
)
def retrieve_dataset(
    dataset_id: int,
    service: Annotated[DatasetService, Depends(DatasetService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
                "datasets:read:all-after-draft",
                "datasets:read:all-after-draft:organisation",
                "datasets:read:all-after-complete",
                "datasets:read:completed",
                "datasets:read:validated",
                "datasets:read:approved",
                "datasets:read:published",
            ]
        )
    ),
) -> ResourceDataset:
    return service.get_dataset(dataset_id, identity)


@router.post("/api/v1/datasets", response_model=ResourceDataset, tags=["dataset"])
def create_dataset(
    dataset_dto: DatasetDto,
    service: Annotated[DatasetService, Depends(DatasetService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
            ]
        )
    ),
) -> ResourceDataset:
    return service.insert_dataset(dataset_dto, identity)


@router.post(
    "/api/v1/datasets/import/rdf",
    response_model=ResourceDataset,
    tags=["dataset"],
    status_code=status.HTTP_201_CREATED,
)
async def import_dataset_from_rdf(
    dataset_import_service: Annotated[
        DatasetRDFImportService, Depends(get_dataset_rdf_import_service)
    ],
    rdf_file: UploadFile = File(...),
    rdf_format: str = Form("turtle"),
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["datasets:edit:draft"])
    ),
) -> ResourceDataset:
    content_bytes = await rdf_file.read()
    if not content_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded RDF file is empty.",
        )

    try:
        rdf_content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RDF file must be UTF-8 encoded.",
        )

    return dataset_import_service.import_dataset(
        rdf_content=rdf_content,
        rdf_format=rdf_format,
        identity=identity,
        duplicates_check=True,
    )


@router.put(
    "/api/v1/datasets/{dataset_id}",
    response_model=ResourceDataset,
    tags=["dataset"],
)
def edit_dataset(
    dataset_id: int,
    dataset_dto: DatasetDto,
    service: Annotated[DatasetService, Depends(DatasetService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
            ]
        )
    ),
) -> ResourceDataset:
    return service.update_dataset(dataset_id, dataset_dto, identity)


@router.post(
    "/api/v1/datasets/{dataset_id}/status/{status_trigger}",
    response_model=ResourceDataset,
    tags=["dataset"],
)
def update_dataset_status(
    dataset_id: int,
    status_trigger: str,
    dataset_status_update_dto: DatasetStatusUpdateDto,
    status_service: DatasetStatusService = Depends(get_status_service),
    comment_service: DatasetCommentService = Depends(DatasetCommentService),
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:status-change:complete",
                "datasets:status-change:complete:my",
                "datasets:status-change:complete:group",
                "datasets:status-change:complete:organisation",
                "datasets:status-change:draft",
                "datasets:status-change:validate",
                "datasets:status-change:approve",
                "datasets:status-change:publish",
                "datasets:status-change:internal-only",
                "datasets:status-change:deprecate",
            ]
        )
    ),
) -> str:
    try:
        response = status_service.update_status(status_trigger)
        if dataset_status_update_dto.comment:
            comment_dto = DatasetCommentDto(
                content=dataset_status_update_dto.comment,
                user_id=identity.user_id,
                dataset_id=dataset_id,
                action_type="add_comment",
            )
            comment_service.add_dataset_comment(comment_dto)
        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/api/v1/datasets/{dataset_id}/versions-chain",
    response_model=List[ResourceDataset],
    tags=["dataset"],
)
def get_dataset_versions_chain(
    dataset_id: int,
    service: Annotated[DatasetService, Depends(DatasetService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
            ]
        )
    ),
) -> List[ResourceDataset]:
    versions = service.get_dataset_versions_chain(dataset_id, identity)
    return [dataset_entity_to_resource(dataset, []) for dataset in versions]


@router.post(
    "/api/v1/datasets/{dataset_id}/version",
    response_model=ResourceDataset,
    tags=["dataset"],
)
def create_dataset_version(
    dataset_id: int,
    service: Annotated[DatasetService, Depends(DatasetService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
            ]
        )
    ),
    version_create_dto: Optional[DatasetVersionCreateDto] = Body(default=None),
) -> ResourceDataset:
    dataset = service.get_dataset(dataset_id, identity)
    if dataset.status != "PUBLISHED":
        raise HTTPException(
            status_code=403, detail="Dataset must be published to create a new version"
        )
    version_change_type = (
        version_create_dto.version_change_type
        if version_create_dto
        else DatasetVersionChangeType.METADATA_ONLY.value
    )
    return service.create_dataset_version(dataset_id, identity, version_change_type)


@router.post(
    "/api/v1/datasets/{dataset_id}/clone",
    response_model=ResourceDataset,
    tags=["dataset"],
)
def clone_dataset(
    dataset_id: int,
    service: Annotated[DatasetService, Depends(DatasetService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
            ]
        )
    ),
) -> ResourceDataset:
    return service.clone_dataset(dataset_id, identity)


@router.delete(
    "/api/v1/datasets/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["dataset"],
)
def delete_dataset(
    dataset_id: int,
    service: Annotated[DatasetService, Depends(DatasetService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:delete:draft:my",
                "datasets:delete:draft:organisation",
                "datasets:delete:draft",
            ]
        )
    ),
) -> Response:
    service.delete_dataset(dataset_id, identity)
    return Response(content=None, status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/api/v1/datasets/{dataset_id}/download",
    tags=["catalogue"],
)
def retrieve_individual_dataset_catalogue(
    service: Annotated[CatalogueService, Depends(CatalogueService)],
    format: CatalogueFormat,
    dataset_id: int,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
                "datasets:read:all-after-draft",
                "datasets:read:all-after-draft:organisation",
                "datasets:read:all-after-complete",
                "datasets:read:completed",
                "datasets:read:validated",
                "datasets:read:approved",
                "datasets:read:published",
            ]
        )
    ),
) -> Response:
    try:
        media_type, content = service.get_individual_dataset_catalogue(
            format, dataset_id, identity
        )
        return Response(
            content=content,
            media_type=media_type,
            status_code=200,
        )
    except Exception as _:
        return ErrorResponse.create(
            status_code=500,
            detail="Failed to retrieve catalogue due to an internal error.",
            title="Catalogue Retrieval Error",
        )
