import os
from typing import Annotated, List, Tuple

from fastapi import Depends
from repositories.authentic_source_label import AuthenticSourceLabelRepository
from schemas.catalogue import CatalogueFormat
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder
from services.catalogues.builders.authentic_source_rdf_builder import (
    AuthenticSourceLabelRDFBuilder,
)
from services.config import ConfigService, get_config_service
from models.authentic_source_label import AuthenticSourceLabel


class AuthenticSourceLabelsCatalogueService:
    def __init__(
        self,
        label_repository: Annotated[
            AuthenticSourceLabelRepository, Depends(AuthenticSourceLabelRepository)
        ],
        config_service: ConfigService = Depends(get_config_service),
    ):
        self._label_repository = label_repository
        self._graph_builder = RDFGraphBuilder(os.getenv("APP_URL"))
        self._label_rdf_builder = AuthenticSourceLabelRDFBuilder(
            self._graph_builder, config_service
        )
        self._config_service = config_service

    def get_catalogue(self, format: CatalogueFormat) -> Tuple[str, str]:
        self._graph_builder.reset()

        self._label_rdf_builder = AuthenticSourceLabelRDFBuilder(
            self._graph_builder, self._config_service
        )

        all_labels = self._label_repository.get_all(include_deprecated=True)
        filtered_labels = self._filter_labels(all_labels)

        for label in filtered_labels:
            self._label_rdf_builder.add_authentic_source_label(label)

        return self._graph_builder.serialize(format)

    def _filter_labels(
        self, labels: List[AuthenticSourceLabel]
    ) -> List[AuthenticSourceLabel]:
        return [label for label in labels if label.assignments]
