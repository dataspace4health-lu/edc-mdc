import os
from typing import Annotated, Tuple

from fastapi import Depends
from repositories.keyword import KeywordRepository
from schemas.catalogue import CatalogueFormat
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder
from services.catalogues.builders.keyword_rdf_builder import KeywordRDFBuilder


class KeywordsCatalogueService:
    def __init__(
        self,
        keyword_repository: Annotated[KeywordRepository, Depends(KeywordRepository)],
    ):
        self._keyword_repository = keyword_repository
        self._graph_builder = RDFGraphBuilder(os.getenv("APP_URL"))
        self._keyword_rdf_builder = KeywordRDFBuilder(self._graph_builder)

    def get_catalogue(self, format: CatalogueFormat) -> Tuple[str, str]:
        self._graph_builder.reset()
        self._keyword_rdf_builder = KeywordRDFBuilder(self._graph_builder)

        all_keywords = self._keyword_repository.get_all()

        for keyword in all_keywords:
            self._keyword_rdf_builder.add_keyword(keyword)

        return self._graph_builder.serialize(format)
