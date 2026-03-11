from typing import Dict
from fastapi import HTTPException, Depends

from repositories.authentic_source_label import AuthenticSourceLabelRepository
from services.authentic_source_labels_catalogue import (
    AuthenticSourceLabelsCatalogueService,
)
from services.front_office.base import BaseFrontOfficeService
from schemas.catalogue import CatalogueFormat
from schemas.front_office_publishing import FrontOfficePublishingResult


class FrontOfficeAuthenticSourcePublishingService(BaseFrontOfficeService):
    def __init__(
        self,
        authentic_source_catalogue_service: AuthenticSourceLabelsCatalogueService = Depends(
            AuthenticSourceLabelsCatalogueService
        ),
        authentic_source_repository: AuthenticSourceLabelRepository = Depends(
            AuthenticSourceLabelRepository
        ),
    ):
        super().__init__()
        self._authentic_source_catalogue_service = authentic_source_catalogue_service
        self._authentic_source_repository = authentic_source_repository

    def generate_and_publish_authentic_source(self) -> FrontOfficePublishingResult:
        catalogue_data = self._generate_catalogue_data()

        return self.publish_files(
            files_data=catalogue_data, base_filename="authentic_source"
        )

    def _generate_catalogue_data(self) -> Dict[str, str]:
        catalogue_data = {}

        try:
            media_type, content = (
                self._authentic_source_catalogue_service.get_catalogue(
                    CatalogueFormat.RDF
                )
            )
            catalogue_data[CatalogueFormat.RDF] = content
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate RDF format: {str(e)} for authentic source label",
            )

        return catalogue_data
