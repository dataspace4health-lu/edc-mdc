from typing import Dict
import asyncio
from fastapi import HTTPException, Depends

from models.identity_context import IdentityContext
from models.dataset import DatasetStatus
from repositories.dataset import DatasetRepository
from services.catalogue import CatalogueService
from services.data_dictionary import DataDictionaryService
from services.front_office.base import BaseFrontOfficeService
from schemas.catalogue import CatalogueFormat
from schemas.front_office_publishing import FrontOfficePublishingResult


class FrontOfficeDatasetPublishingService(BaseFrontOfficeService):
    def __init__(
        self,
        catalogue_service: CatalogueService = Depends(CatalogueService),
        data_dictionary_service: DataDictionaryService = Depends(DataDictionaryService),
        dataset_repository: DatasetRepository = Depends(DatasetRepository),
    ):
        super().__init__()
        self._catalogue_service = catalogue_service
        self._data_dictionary_service = data_dictionary_service
        self._dataset_repository = dataset_repository

    def generate_and_publish_dataset_catalogues(
        self, dataset_id: int, identity: IdentityContext
    ) -> FrontOfficePublishingResult:
        dataset = self._validate_dataset(dataset_id)
        catalogue_data = self._generate_catalogue_data(dataset_id, identity)

        # Generate data dictionary CSV if it exists
        data_dictionary_csv = self._generate_data_dictionary_csv(dataset_id, identity)
        if data_dictionary_csv:
            catalogue_data["CSV"] = data_dictionary_csv

        return self.publish_files(
            files_data=catalogue_data,
            base_filename=dataset.identifier,
            dataset_id=dataset_id,
        )

    def _validate_dataset(self, dataset_id: int):
        dataset = self._dataset_repository.get_dataset_by_id(dataset_id)

        if not dataset:
            raise HTTPException(
                status_code=404, detail=f"Dataset with id {dataset_id} not found"
            )

        # Allow published datasets, approved datasets that were previously published, or deprecated datasets
        is_published = dataset.status == DatasetStatus.PUBLISHED.value
        is_previously_published_approved = (
            dataset.status == DatasetStatus.APPROVED.value
            and dataset.released_at is not None
        )
        is_deprecated = dataset.status == DatasetStatus.DEPRECATED.value

        if not (is_published or is_previously_published_approved or is_deprecated):
            raise HTTPException(
                status_code=400,
                detail="Dataset must be PUBLISHED, APPROVED with previous publication, or DEPRECATED to generate catalogue for front office",
            )

        return dataset

    def _generate_catalogue_data(
        self, dataset_id: int, identity: IdentityContext
    ) -> Dict[str, str]:
        catalogue_data = {}
        formats = [CatalogueFormat.RDF, CatalogueFormat.TTL, CatalogueFormat.JSONLD]

        # Generate master RDF file with all versions for front office HTML generation
        try:
            media_type, master_content = (
                self._catalogue_service.get_individual_dataset_catalogue(
                    CatalogueFormat.RDF,
                    dataset_id,
                    identity,
                    include_versions=True,
                    include_status=True,
                )
            )
            catalogue_data["RDF_MASTER"] = master_content
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate master RDF format: {str(e)} for dataset {dataset_id}",
            )

        # Generate export files (DCAT-AP compliant, without versions)
        for format_type in formats:
            try:
                media_type, content = (
                    self._catalogue_service.get_individual_dataset_catalogue(
                        format_type, dataset_id, identity, include_versions=False
                    )
                )
                catalogue_data[format_type] = content
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate {format_type} format: {str(e)} for dataset {dataset_id}",
                )

        return catalogue_data

    def _generate_data_dictionary_csv(
        self, dataset_id: int, identity: IdentityContext
    ) -> str:
        try:
            # Check if data dictionaries exist for this dataset
            data_dictionaries = (
                self._data_dictionary_service.get_data_dictionaries_by_dataset_id(
                    dataset_id, identity
                )
            )

            if not data_dictionaries:
                return None

            # Generate CSV content using async iteration
            return asyncio.run(self._generate_csv_content_async(dataset_id, identity))

        except Exception as e:
            # For data dictionary, we don't fail the whole operation but log the issue
            print(f"Warning: Failed to generate data dictionary CSV: {str(e)}")
            return None

    async def _generate_csv_content_async(
        self, dataset_id: int, identity: IdentityContext
    ) -> str:
        csv_response = self._data_dictionary_service.generate_csv(dataset_id, identity)

        csv_content = ""
        async for chunk in csv_response.body_iterator:
            if isinstance(chunk, bytes):
                csv_content += chunk.decode("utf-8")
            else:
                csv_content += str(chunk)

        return csv_content
