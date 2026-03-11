import os
from datetime import datetime
from typing import Annotated, List, Tuple

from fastapi import Depends
from models.dataset import Dataset
from models.data_service import DataService
from models.identity_context import IdentityContext
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF
from repositories.dataset import DatasetRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.data_service import DataServiceRepository
from repositories.data_dictionary import DataDictionaryRepository
from services.config import ConfigService, get_config_service
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder
from services.catalogues.builders.catalogue_rdf_builder import CatalogueRDFBuilder
from services.catalogues.builders.distribution_rdf_builder import DistributionRDFBuilder
from services.catalogues.builders.dataset_rdf_builder import DatasetRDFBuilder
from services.dataset_permissions_service import DatasetPermissionsService


class CatalogueService:
    def __init__(
        self,
        dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)],
        applicable_legislation_repository: Annotated[
            ApplicableLegislationRepository, Depends(ApplicableLegislationRepository)
        ],
        data_service_repository: Annotated[
            DataServiceRepository, Depends(DataServiceRepository)
        ],
        data_dictionary_repository: Annotated[
            DataDictionaryRepository, Depends(DataDictionaryRepository)
        ],
        dataset_permissions_service: Annotated[
            DatasetPermissionsService, Depends(DatasetPermissionsService)
        ],
        config_service: ConfigService = Depends(get_config_service),
    ):
        self._dataset_repository = dataset_repository
        self._applicable_legislation_repository = applicable_legislation_repository
        self._data_service_repository = data_service_repository
        self._data_dictionary_repository = data_dictionary_repository
        self._dataset_permissions_service = dataset_permissions_service
        self._config_service = config_service
        catalogue_config = config_service.get_catalogue()
        catalogue_url = catalogue_config["url"]
        uri_templates = catalogue_config["uri_templates"]
        hdab_config = config_service.get_health_data_access_body()
        self._graph_builder = RDFGraphBuilder(catalogue_url, uri_templates, hdab_config)
        self._catalogue_rdf_builder = CatalogueRDFBuilder(
            self._graph_builder,
            config_service,
        )
        self._dataset_rdf_builder = DatasetRDFBuilder(
            self._graph_builder,
            self._applicable_legislation_repository,
            self._data_dictionary_repository,
        )
        self._distribution_rdf_builder = DistributionRDFBuilder(
            self._graph_builder,
            self._applicable_legislation_repository,
        )

    def get_individual_dataset_catalogue(
        self,
        format: str,
        dataset_id: int,
        identity: IdentityContext,
        include_versions: bool = False,
        include_status: bool = False,
    ) -> Tuple[str, str]:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )

        graph = self._graph_builder.get_graph()

        target_dataset: Dataset | None = None
        history_versions: List[Dataset] = []

        if include_versions:
            all_versions = self._dataset_repository.get_all_versions_of_dataset(
                dataset_id
            )
            if all_versions:
                target_dataset = next(
                    (dataset for dataset in all_versions if dataset.id == dataset_id),
                    None,
                )
                if target_dataset is None:
                    target_dataset = max(
                        all_versions,
                        key=lambda d: getattr(d, "submitted_at", datetime.min),
                    )
                history_versions = [
                    version
                    for version in all_versions
                    if version.id != target_dataset.id
                ]
            else:
                target_dataset = self._dataset_repository.get_dataset_by_id(dataset_id)
        else:
            target_dataset = self._dataset_repository.get_dataset_by_id(dataset_id)

        data_services = self._data_service_repository.get_data_services()

        if target_dataset:
            sorted_history = (
                sorted(
                    history_versions,
                    key=lambda d: getattr(d, "submitted_at", datetime.min),
                    reverse=True,
                )
                if history_versions
                else []
            )
            self._add_dataset(
                target_dataset,
                include_status,
                add_to_catalogue=False,
                version_history=sorted_history,
            )

        # Add data services (referenced by distributions)
        for data_service in data_services:
            self._add_data_service(graph, data_service)

        return self._graph_builder.serialize(format)

    def get_catalogue(
        self, format: str, only_non_public_access: bool = False
    ) -> Tuple[str, str]:
        graph = self._graph_builder.get_graph()
        datasets = self._dataset_repository.get_public_datasets(only_non_public_access)
        data_services = self._data_service_repository.get_data_services()

        self._catalogue_rdf_builder.add_catalogue_metadata(datasets, data_services)

        # First add all datasets and services as resources
        for dataset in datasets:
            self._add_dataset(dataset)

        # Add data services as top-level resources first
        for data_service in data_services:
            self._add_data_service(graph, data_service)

        return self._graph_builder.serialize(format)

    def _add_dataset(
        self,
        dataset: Dataset,
        include_status: bool = False,
        add_to_catalogue: bool = True,
        version_history: List[Dataset] | None = None,
    ):
        dataset_uri = self._dataset_rdf_builder.add_dataset(
            dataset,
            include_status,
            add_to_catalogue,
            distribution_builder=self._distribution_rdf_builder,
        )

        if version_history:
            self._dataset_rdf_builder.add_version_history(
                dataset_uri, version_history, self._distribution_rdf_builder
            )

        return dataset_uri

    def _add_data_service(self, graph: Graph, data_service: DataService):
        data_service_uri = self._graph_builder.get_data_service_uri(data_service.id)
        graph.add((data_service_uri, RDF.type, DCAT.DataService))
        graph.add(
            (
                data_service_uri,
                DCTERMS.title,
                Literal(lang="eng", lexical_or_value=data_service.title),
            )
        )

        for endpoint in data_service.endpoints:
            graph.add(
                (data_service_uri, DCAT.endpointURL, URIRef(endpoint.endpoint_url))
            )

            if endpoint.endpoint_description:
                # dcat:endpointDescription must be a URI - only add if it's a valid URL
                desc = str(endpoint.endpoint_description).strip()
                if desc.startswith(("http://", "https://", "ftp://")):
                    graph.add(
                        (
                            data_service_uri,
                            DCAT.endpointDescription,
                            URIRef(desc),
                        )
                    )
