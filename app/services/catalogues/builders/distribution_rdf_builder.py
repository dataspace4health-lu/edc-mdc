"""RDF builder for distribution entities."""

from rdflib import BNode, Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, RDFS, XSD, SKOS

from models.distribution import Distribution
from models.dataset import Dataset
from repositories.applicable_legislation import ApplicableLegislationRepository
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder
from services.catalogues.mappers.namespace_constants import (
    EU_R5R,
    SPDX,
    ODRL,
    DUO,
    ADMS,
    HEALTHDCATAP,
)
from services.catalogues.mappers.type_mappers import TypeMappers


class DistributionRDFBuilder:
    def __init__(
        self,
        graph_builder: RDFGraphBuilder,
        applicable_legislation_repository: ApplicableLegislationRepository,
    ):
        self.graph_builder = graph_builder
        self.graph = graph_builder.get_graph()
        self.applicable_legislation_repository = applicable_legislation_repository

    def add_distribution(self, dataset_uri: URIRef, distribution: Distribution) -> None:
        if distribution.internal_only:
            return

        # Use blank node to force inline nesting in XML serialization
        distribution_uri = BNode()

        if distribution.is_analytics:
            self.graph.add((dataset_uri, HEALTHDCATAP.analytics, distribution_uri))
        else:
            self.graph.add((dataset_uri, DCAT.distribution, distribution_uri))

        self.graph.add((distribution_uri, RDF.type, DCAT.Distribution))

        # Add identifier to preserve distribution ID information
        self.graph.add((distribution_uri, DCTERMS.identifier, Literal(distribution.id)))

        self._add_basic_properties(distribution_uri, distribution)
        self._add_access_services(distribution_uri, distribution)
        self._add_format_info(distribution_uri, distribution)
        self._add_languages(distribution_uri, distribution)
        self._add_temporal_info(distribution_uri, distribution)
        self._add_urls(distribution_uri, distribution)
        self._add_rights_and_licensing(distribution_uri, distribution)
        self._add_legal_information(distribution_uri, distribution)
        self._add_policy_info(distribution_uri, distribution)
        self._add_additional_metadata(distribution_uri, distribution)
        self._add_schemas(distribution_uri, distribution)
        self._add_status_info(distribution_uri, distribution)
        self._add_resolution_info(distribution_uri, distribution)

    def add_data_dictionary_sample_distribution(
        self, dataset_uri: URIRef, dataset: Dataset
    ) -> None:
        # Use blank node to force inline nesting in XML serialization
        dd_distribution_uri = BNode()

        # Link sample distributions both through dcat:distribution and adms:sample
        self.graph.add((dataset_uri, DCAT.distribution, dd_distribution_uri))
        self.graph.add((dataset_uri, ADMS.sample, dd_distribution_uri))
        self.graph.add((dd_distribution_uri, RDF.type, DCAT.Distribution))

        self.graph.add(
            (
                dd_distribution_uri,
                DCTERMS.title,
                Literal(
                    lang="eng", lexical_or_value=f"Data Dictionary for {dataset.title}"
                ),
            )
        )

        self.graph.add(
            (
                dd_distribution_uri,
                DCTERMS.description,
                Literal(
                    lang="eng",
                    lexical_or_value="Machine-readable data dictionary describing the structure and contents of the dataset.",
                ),
            )
        )

        format_uri = "http://publications.europa.eu/resource/authority/file-type/CSV"
        self.graph_builder.add_uri_resource_with_label(
            dd_distribution_uri,
            DCTERMS.format,
            DCTERMS.MediaTypeOrExtent,
            format_uri,
        )

        media_type_uri = "http://www.iana.org/assignments/media-types/text/csv"
        self.graph_builder.add_uri_resource_with_label(
            dd_distribution_uri,
            DCAT.mediaType,
            DCTERMS.MediaType,
            media_type_uri,
        )

        access_url = self.graph_builder.get_sample_distribution_download_uri(
            dataset.identifier
        )
        self.graph.add((dd_distribution_uri, DCAT.accessURL, access_url))

        self.graph.add((dd_distribution_uri, DCAT.downloadURL, access_url))

        license_uri = "http://creativecommons.org/publicdomain/zero/1.0/"
        self.graph_builder.add_uri_resource_with_label(
            dd_distribution_uri,
            DCTERMS.license,
            DCTERMS.LicenseDocument,
            license_uri,
        )

        availability_uri = "http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE"
        self.graph_builder.add_uri_resource_with_label(
            dd_distribution_uri,
            EU_R5R.availability,
            SKOS.Concept,
            availability_uri,
            "Available",
        )

    def _add_basic_properties(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        if distribution.description:
            self.graph.add(
                (
                    distribution_uri,
                    DCTERMS.description,
                    Literal(lang="eng", lexical_or_value=distribution.description),
                )
            )

        self.graph.add(
            (
                distribution_uri,
                DCTERMS.title,
                Literal(lang="eng", lexical_or_value=distribution.title),
            )
        )

    def _add_access_services(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        if distribution.access_services:
            for access_service in distribution.access_services:
                service_uri = self.graph_builder.get_data_service_uri(
                    access_service.data_service.id
                )
                self.graph.add((distribution_uri, DCAT.accessService, service_uri))

    def _add_format_info(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        if distribution.file_type:
            self.graph_builder.add_uri_resource_with_label(
                distribution_uri,
                DCTERMS.format,
                DCTERMS.MediaTypeOrExtent,
                distribution.file_type,
            )

        if distribution.media_type:
            base_uri = "http://www.iana.org/assignments/media-types/"
            self.graph_builder.add_uri_resource_with_label(
                distribution_uri,
                DCAT.mediaType,
                DCTERMS.MediaType,
                base_uri + distribution.media_type,
            )

        if distribution.compression_format:
            base_uri = "http://www.iana.org/assignments/media-types/"
            self.graph_builder.add_uri_resource_with_label(
                distribution_uri,
                DCAT.compressFormat,
                DCTERMS.MediaType,
                base_uri + distribution.compression_format,
            )

        if distribution.packaging_format:
            base_uri = "http://www.iana.org/assignments/media-types/"
            self.graph_builder.add_uri_resource_with_label(
                distribution_uri,
                DCAT.packageFormat,
                DCTERMS.MediaType,
                base_uri + distribution.packaging_format,
            )

    def _add_languages(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        for language in distribution.languages:
            self.graph_builder.add_language(distribution_uri, language.key)

    def _add_temporal_info(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        if distribution.release_date:
            self.graph.add(
                (
                    distribution_uri,
                    DCTERMS.issued,
                    Literal(
                        datatype=XSD.dateTime,
                        lexical_or_value=distribution.release_date.isoformat(),
                    ),
                )
            )

        if distribution.modification_date:
            self.graph.add(
                (
                    distribution_uri,
                    DCTERMS.modified,
                    Literal(
                        datatype=XSD.dateTime,
                        lexical_or_value=distribution.modification_date.isoformat(),
                    ),
                )
            )

    def _add_urls(self, distribution_uri: URIRef, distribution: Distribution) -> None:
        if distribution.download_urls:
            for download_urls_entity in distribution.download_urls:
                download_urls = URIRef(download_urls_entity.url)
                self.graph.add((distribution_uri, DCAT.downloadURL, download_urls))

        if distribution.access_urls:
            for access_url_entity in distribution.access_urls:
                access_url = URIRef(access_url_entity.url)
                self.graph.add((distribution_uri, DCAT.accessURL, access_url))

    def _add_rights_and_licensing(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        if distribution.rights_statement:
            self.graph_builder.add_uri_resource_with_label(
                distribution_uri,
                DCTERMS.rights,
                DCTERMS.RightsStatement,
                distribution.rights_statement,
            )

        if distribution.license:
            license_uri = f"http://spdx.org/licenses/{distribution.license}"
            self.graph_builder.add_uri_resource_with_label(
                distribution_uri,
                DCTERMS.license,
                DCTERMS.LicenseDocument,
                license_uri,
            )

    def _add_legal_information(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        # Applicable legislation
        if distribution.applicable_legislations:
            applicable_legislations = self.applicable_legislation_repository.get_all()
            for legislation in distribution.applicable_legislations:
                self.graph_builder.add_legal_resource(
                    distribution_uri,
                    legislation,
                    applicable_legislations,
                    lambda x, key: x.eng_label if x.key == key else None,
                )

    def _add_policy_info(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        policy_actions = getattr(distribution, "policy_actions", [])

        if not policy_actions:
            return

        policy_node = BNode()
        self.graph.add((distribution_uri, ODRL.hasPolicy, policy_node))
        # Explicitly type the policy to satisfy validators expecting odrl:Policy
        self.graph.add((policy_node, RDF.type, ODRL.Policy))
        self.graph.add((policy_node, RDF.type, ODRL.Set))

        for action in policy_actions:
            rule_node = BNode()
            if action.policy_action_type == "permission":
                self.graph.add((policy_node, ODRL.permission, rule_node))
                self.graph.add((rule_node, RDF.type, ODRL.Permission))
            else:
                self.graph.add((policy_node, ODRL.prohibition, rule_node))
                self.graph.add((rule_node, RDF.type, ODRL.Prohibition))

            self.graph.add((rule_node, ODRL.action, ODRL.use))

            constraint_type = action.policy_constraint_type

            if constraint_type == "temporal":
                self._add_temporal_constraint(rule_node, action)
            elif constraint_type == "spatial":
                self._add_spatial_constraint(rule_node, action)
            elif constraint_type in ["purpose", "industry"]:
                self._add_other_constraint(rule_node, action)

    def _add_temporal_constraint(self, rule_node: BNode, action) -> None:
        date_time_operand = ODRL.dateTime

        if action.temporal_restriction_start:
            start = BNode()
            self.graph.add((rule_node, ODRL.constraint, start))
            self.graph.add((start, ODRL.leftOperand, date_time_operand))
            self.graph.add((start, ODRL.operator, ODRL.gteq))
            self.graph.add(
                (
                    start,
                    ODRL.rightOperand,
                    Literal(
                        action.temporal_restriction_start.isoformat(),
                        datatype=XSD.date,
                    ),
                )
            )

        if action.temporal_restriction_end:
            end = BNode()
            self.graph.add((rule_node, ODRL.constraint, end))
            self.graph.add((end, ODRL.leftOperand, date_time_operand))
            self.graph.add((end, ODRL.operator, ODRL.lteq))
            self.graph.add(
                (
                    end,
                    ODRL.rightOperand,
                    Literal(
                        action.temporal_restriction_end.isoformat(),
                        datatype=XSD.date,
                    ),
                )
            )

    def _add_spatial_constraint(self, rule_node: BNode, action) -> None:
        spatial_restrictions = getattr(action, "spatial_restrictions", [])

        for spatial_restriction in spatial_restrictions:
            c = BNode()
            self.graph.add((rule_node, ODRL.constraint, c))
            self.graph.add((c, ODRL.leftOperand, DCTERMS.spatial))
            self.graph.add((c, ODRL.operator, ODRL.eq))
            restriction_value = getattr(spatial_restriction, "value", None)
            if restriction_value:
                self.graph.add((c, ODRL.rightOperand, Literal(restriction_value.key)))

    def _add_other_constraint(self, rule_node: BNode, action) -> None:
        c = BNode()
        self.graph.add((rule_node, ODRL.constraint, c))
        self.graph.add((c, ODRL.operator, ODRL.eq))

        constraint_type = action.policy_constraint_type
        constraint_value = action.policy_constraint_value

        if constraint_type == "purpose":
            self.graph.add((c, ODRL.leftOperand, ODRL.purpose))
            duo_code = constraint_value.replace(":", "_")
            self.graph.add((c, ODRL.rightOperand, DUO[duo_code]))

        elif constraint_type == "industry":
            self.graph.add(
                (
                    c,
                    ODRL.leftOperand,
                    URIRef("http://www.w3.org/ns/odrl/2/industry"),  # NOSONAR
                )
            )
            self.graph.add((c, ODRL.rightOperand, Literal(constraint_value)))

    def _add_additional_metadata(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        if distribution.availability:
            self._add_availability_node(
                distribution_uri,
                distribution.availability,
            )

        if distribution.documentation_entries:
            for doc in distribution.documentation_entries:
                self.graph_builder.add_document(distribution_uri, FOAF.page, doc.value)

        if distribution.byte_size:
            self.graph.add(
                (
                    distribution_uri,
                    DCAT.byteSize,
                    Literal(distribution.byte_size, datatype=XSD.nonNegativeInteger),
                )
            )

        if distribution.checksum:
            checksum_node = BNode()
            self.graph.add((distribution_uri, SPDX.checksum, checksum_node))
            self.graph.add((checksum_node, RDF.type, SPDX.Checksum))
            self.graph.add((checksum_node, SPDX.algorithm, SPDX.checksumAlgorithm_sha1))
            self.graph.add(
                (
                    checksum_node,
                    SPDX.checksumValue,
                    Literal(distribution.checksum, datatype=XSD.hexBinary),
                )
            )

    def _add_schemas(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        for schema in distribution.linked_schemas:
            standard_uri = URIRef(schema.key)
            self.graph.add((distribution_uri, DCTERMS.conformsTo, standard_uri))
            self.graph.add((standard_uri, RDF.type, DCTERMS.Standard))

    def _add_status_info(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        if distribution.distribution_dcat_status:
            status_uri = URIRef(
                f"http://publications.europa.eu/resource/authority/distribution-status/{distribution.distribution_dcat_status.value.upper()}"  # NOSONAR
            )
            # Use named URI with label for convenience
            self.graph.add((distribution_uri, ADMS.status, status_uri))
            # Add type declaration for DCAT-AP compliance
            self.graph.add((status_uri, RDF.type, SKOS.Concept))
            self.graph.add(
                (
                    status_uri,
                    SKOS.prefLabel,
                    Literal(distribution.distribution_dcat_status.value, lang="eng"),
                )
            )

    def _add_resolution_info(
        self, distribution_uri: URIRef, distribution: Distribution
    ) -> None:
        # Spatial resolution
        if distribution.spatial_resolution:
            self.graph.add(
                (
                    distribution_uri,
                    DCAT.spatialResolutionInMeters,
                    Literal(
                        datatype=XSD.decimal,
                        lexical_or_value=distribution.spatial_resolution,
                    ),
                )
            )

        # Temporal resolution
        if distribution.temporal_resolution:
            self.graph.add(
                (
                    distribution_uri,
                    DCAT.temporalResolution,
                    Literal(
                        datatype=XSD.duration,
                        lexical_or_value=distribution.temporal_resolution,
                    ),
                )
            )

    def _add_availability_node(self, dist_uri: URIRef, availability_uri: str) -> None:
        label = TypeMappers.map_availability(availability_uri)
        self.graph_builder.add_uri_resource_with_label(
            dist_uri,
            EU_R5R.availability,
            SKOS.Concept,
            availability_uri,
            label,
        )
