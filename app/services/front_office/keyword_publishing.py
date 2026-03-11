from typing import Dict
from fastapi import HTTPException, Depends

from repositories.keyword import KeywordRepository
from services.keywords_catalogue import KeywordsCatalogueService
from services.front_office.base import BaseFrontOfficeService
from schemas.catalogue import CatalogueFormat
from schemas.front_office_publishing import FrontOfficePublishingResult


class FrontOfficeKeywordPublishingService(BaseFrontOfficeService):
    def __init__(
        self,
        keyword_catalogue_service: KeywordsCatalogueService = Depends(
            KeywordsCatalogueService
        ),
        keyword_repository: KeywordRepository = Depends(KeywordRepository),
    ):
        super().__init__()
        self._keyword_catalogue_service = keyword_catalogue_service
        self._keyword_repository = keyword_repository

    def generate_and_publish_keywords(self) -> FrontOfficePublishingResult:
        catalogue_data = self._generate_catalogue_data()

        return self.publish_files(files_data=catalogue_data, base_filename="keywords")

    def _generate_catalogue_data(self) -> Dict[str, str]:
        catalogue_data = {}

        try:
            media_type, content = self._keyword_catalogue_service.get_catalogue(
                CatalogueFormat.RDF
            )
            catalogue_data[CatalogueFormat.RDF] = content
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate RDF format: {str(e)} for keywords",
            )

        return catalogue_data
