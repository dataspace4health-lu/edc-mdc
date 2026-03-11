from fastapi import APIRouter, Depends, status, File, UploadFile, HTTPException
from services.data_dictionary import DataDictionaryService
from services.antivirus import AntivirusService
from schemas.data_dictionary import (
    ResourceDataDictionaryEntry,
    BulkUpdateAuthenticSourceDto,
    BulkUpdatePositionDto,
)
from typing import List, Annotated
from fastapi.responses import Response
from routes.auth import validate_and_retrieve_identity_context
from models.identity_context import IdentityContext
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.get(
    "/api/v1/datasets/{dataset_id}/data-dictionaries",
    response_model=List[ResourceDataDictionaryEntry],
    tags=["data-dictionaries"],
)
def get_data_dictionaries_by_dataset_id(
    dataset_id: int,
    service: Annotated[DataDictionaryService, Depends(DataDictionaryService)],
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
) -> List[ResourceDataDictionaryEntry]:
    return service.get_data_dictionaries_by_dataset_id(dataset_id, identity)


@router.post(
    "/api/v1/datasets/{dataset_id}/data-dictionaries",
    response_model=ResourceDataDictionaryEntry,
    tags=["data-dictionaries"],
    status_code=status.HTTP_201_CREATED,
)
def add_data_dictionary(
    dataset_id: int,
    data: ResourceDataDictionaryEntry,
    service: Annotated[DataDictionaryService, Depends(DataDictionaryService)],
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
) -> ResourceDataDictionaryEntry:
    return service.add_data_dictionary(dataset_id, data, identity)


@router.put(
    "/api/v1/datasets/{dataset_id}/data-dictionaries/{entry_id}",
    response_model=ResourceDataDictionaryEntry,
    tags=["data-dictionaries"],
    status_code=status.HTTP_200_OK,
)
def update_data_dictionary(
    dataset_id: int,
    entry_id: int,
    data: ResourceDataDictionaryEntry,
    service: Annotated[DataDictionaryService, Depends(DataDictionaryService)],
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
) -> ResourceDataDictionaryEntry:
    return service.update_data_dictionary(dataset_id, entry_id, data, identity)


@router.delete(
    "/api/v1/datasets/{dataset_id}/data-dictionaries/{entry_id}",
    tags=["data-dictionaries"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_data_dictionary_entry(
    dataset_id: int,
    entry_id: int,
    service: Annotated[DataDictionaryService, Depends(DataDictionaryService)],
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
) -> Response:
    service.delete_data_dictionary_entry(dataset_id, entry_id, identity)
    return Response(content=None, status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-upload",
    tags=["data-dictionaries"],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_upload_data_dictionaries(
    dataset_id: int,
    service: Annotated[DataDictionaryService, Depends(DataDictionaryService)],
    antivirus_service: Annotated[AntivirusService, Depends(AntivirusService)],
    file: UploadFile = File(...),
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
) -> dict:
    # Scan file for viruses
    is_clean, message = await antivirus_service.scan_file(file)
    if not is_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File scan failed: {message}",
        )

    return await service.bulk_upload_data_dictionaries(dataset_id, file, identity)


@router.get(
    "/api/v1/datasets/{dataset_id}/data-dictionaries/download",
    tags=["data-dictionaries"],
    response_class=StreamingResponse,
)
def download_data_dictionary_csv(
    dataset_id: int,
    service: Annotated[DataDictionaryService, Depends(DataDictionaryService)],
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
) -> StreamingResponse:
    return service.generate_csv(dataset_id, identity)


@router.post(
    "/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-update-authentic-source",
    response_model=List[ResourceDataDictionaryEntry],
    tags=["data-dictionaries"],
    status_code=status.HTTP_200_OK,
)
def bulk_update_authentic_source(
    dataset_id: int,
    update_data: BulkUpdateAuthenticSourceDto,
    service: Annotated[DataDictionaryService, Depends(DataDictionaryService)],
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
) -> List[ResourceDataDictionaryEntry]:
    return service.bulk_update_authentic_source(dataset_id, update_data, identity)


@router.post(
    "/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-update-positions",
    response_model=List[ResourceDataDictionaryEntry],
    tags=["data-dictionaries"],
    status_code=status.HTTP_200_OK,
)
def bulk_update_positions(
    dataset_id: int,
    update_data: BulkUpdatePositionDto,
    service: Annotated[DataDictionaryService, Depends(DataDictionaryService)],
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
) -> List[ResourceDataDictionaryEntry]:
    return service.bulk_update_positions(dataset_id, update_data, identity)
