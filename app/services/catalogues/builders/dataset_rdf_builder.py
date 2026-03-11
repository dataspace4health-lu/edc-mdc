import re
from typing import TYPE_CHECKING, List, Optional
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, RDFS, XSD, SKOS

from models.dataset import Dataset, DatasetStatus
from repositories.data_dictionary import DataDictionaryRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from services.catalogues.mappers.namespace_constants import (
    VCARD,
    CSVW,
    EU_R5R,
    DPV,
    ADMS,
    PROV,
    CDSP,
    HEALTHDCATAP,
    HEALTH_VOCABULARY_BASE,
    DPVPD,
)
from services.catalogues.mappers.type_mappers import TypeMappers
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder

if TYPE_CHECKING:
    from models.dataset_relation import DatasetRelationEntry
    from services.catalogues.builders.distribution_rdf_builder import (
        DistributionRDFBuilder,
    )


class DatasetRDFBuilder:
    def __init__(
        self,
        graph_builder: RDFGraphBuilder,
        applicable_legislation_repository: ApplicableLegislationRepository,
        data_dictionary_repository: DataDictionaryRepository,
    ):
        self.graph_builder = graph_builder
        self.graph = graph_builder.get_graph()
        self.applicable_legislation_repository = applicable_legislation_repository
        self.data_dictionary_repository = data_dictionary_repository

    def add_dataset(
        self,
        dataset: Dataset,
        include_status: bool = False,
        add_to_catalogue: bool = True,
        distribution_builder: Optional["DistributionRDFBuilder"] = None,
    ) -> URIRef:
        catalogue_uri = self.graph_builder.get_catalogue_uri()

        # Determine if this is the latest version
        # A dataset is NOT the latest if it has next_versions
        is_latest_version = True
        try:
            if hasattr(dataset, "next_versions") and dataset.next_versions is not None:
                next_vers = dataset.next_versions
                # Check if it's a real list/collection with items
                if next_vers is not None and len(next_vers) > 0:
                    is_latest_version = False
        except Exception:
            # If any error occurs, assume it's the latest version
            is_latest_version = True

        # Generate version number by counting position in version chain
        version_number = None
        if not is_latest_version:
            # Count versions by traversing backward through the chain (max 100 to prevent infinite loops)
            count = 1
            current = dataset
            visited = set()
            visited.add(id(current))
            max_iterations = 100

            while count < max_iterations:
                try:
                    if not hasattr(current, "previous_version"):
                        break
                    prev = current.previous_version
                    if not prev:
                        break
                    # Break if we've seen this object before (circular reference)
                    if id(prev) in visited:
                        break
                    visited.add(id(prev))
                    count += 1
                    current = prev
                except:
                    # If any error occurs, stop traversing
                    break
            version_number = str(count)

        dataset_uri = self.graph_builder.get_dataset_uri(
            dataset.identifier,
            is_latest_version=is_latest_version,
            version_number=version_number,
        )

        # Only add dataset to catalogue if requested (for full catalogue RDF)
        if add_to_catalogue:
            self.graph.add((catalogue_uri, DCAT.dataset, dataset_uri))

        self._render_dataset_contents(
            dataset_uri,
            dataset,
            include_status,
            distribution_builder=distribution_builder,
        )

        return dataset_uri

    def _render_dataset_contents(
        self,
        subject_uri: URIRef,
        dataset: Dataset,
        include_status: bool,
        distribution_builder: Optional["DistributionRDFBuilder"],
    ) -> None:
        self._add_dataset_type(subject_uri, dataset)
        self._add_basic_properties(subject_uri, dataset)
        self._add_themes(subject_uri, dataset)
        self._add_health_categories(subject_uri, dataset)
        self._add_health_themes(subject_uri, dataset)
        self._add_typical_age(subject_uri, dataset)
        self._add_number_of_records(subject_uri, dataset)
        self._add_number_of_unique_individuals(subject_uri, dataset)
        self._add_population_coverage(subject_uri, dataset)
        self._add_code_values(subject_uri, dataset)
        self._add_purpose(subject_uri, dataset)
        self._add_coding_systems(subject_uri, dataset)
        self._add_health_data_access_body(subject_uri, dataset)
        self._add_health_legal_basis(subject_uri, dataset)
        self._add_qualified_attributions(subject_uri, dataset)
        self._add_spatial_coverage(subject_uri, dataset)
        self._add_legal_information(subject_uri, dataset)
        self._add_dataset_types(subject_uri, dataset)
        self._add_temporal_information(subject_uri, dataset)
        self._add_creator(subject_uri, dataset)
        self._add_provenance(subject_uri, dataset)
        self._add_languages(subject_uri, dataset)
        self._add_other_properties(subject_uri, dataset)
        self._add_publisher_and_contact(subject_uri, dataset)
        self._add_temporal_period(subject_uri, dataset)
        self._add_retention_period(subject_uri, dataset)
        self._add_relations(subject_uri, dataset)
        self._add_dataset_series_info(subject_uri, dataset)
        self._add_keywords(subject_uri, dataset)
        self._add_authentic_sources(subject_uri, dataset)
        self._add_personal_data(subject_uri, dataset)

        self._add_data_dictionary(subject_uri, dataset)
        if distribution_builder is not None and getattr(
            dataset, "data_dictionaries", None
        ):
            distribution_builder.add_data_dictionary_sample_distribution(
                subject_uri, dataset
            )

        if distribution_builder is not None and getattr(dataset, "distributions", None):
            for distribution in dataset.distributions:
                if getattr(distribution, "internal_only", False):
                    continue
                distribution_builder.add_distribution(subject_uri, distribution)

        if include_status:
            self._add_status(subject_uri, dataset)

    def add_version_history(
        self,
        dataset_uri: URIRef,
        versions: List["Dataset"],
        distribution_builder: Optional["DistributionRDFBuilder"] = None,
    ) -> None:
        if not versions:
            return

        for version in versions:
            entry_node = BNode()
            self.graph.add((dataset_uri, CDSP.history, entry_node))
            self._render_dataset_contents(
                entry_node,
                version,
                include_status=False,
                distribution_builder=distribution_builder,
            )

    def _add_dataset_type(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.is_dataset_series and not any(dataset.series_memberships):
            self.graph.add((dataset_uri, RDF.type, DCAT.DatasetSeries))
        else:
            self.graph.add((dataset_uri, RDF.type, DCAT.Dataset))

    def _add_basic_properties(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        # Title
        self.graph.add(
            (
                dataset_uri,
                DCTERMS.title,
                Literal(lang="eng", lexical_or_value=dataset.title),
            )
        )

        # Description
        self.graph.add(
            (
                dataset_uri,
                DCTERMS.description,
                Literal(lang="eng", lexical_or_value=dataset.description),
            )
        )

        # Identifier
        self.graph.add((dataset_uri, DCTERMS.identifier, Literal(dataset.identifier)))

        # Periodicity
        if dataset.periodicity:
            self.graph_builder.add_uri_resource_with_label(
                dataset_uri,
                DCTERMS.accrualPeriodicity,
                DCTERMS.Frequency,
                dataset.periodicity,
            )

        # Access rights
        self.graph_builder.add_uri_resource_with_label(
            dataset_uri,
            DCTERMS.accessRights,
            DCTERMS.RightsStatement,
            dataset.rights_statement,
        )

    def _add_themes(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        for theme in dataset.themes:
            self.graph_builder.add_uri_resource_with_label(
                dataset_uri, DCAT.theme, SKOS.Concept, theme.key, theme.value.eng_label
            )

    def _add_health_categories(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        for health_category in dataset.health_categories:
            category_uri = (
                f"{HEALTH_VOCABULARY_BASE}healthcategories/{health_category.key}"
            )
            self.graph_builder.add_uri_resource_with_label(
                dataset_uri,
                HEALTHDCATAP.healthCategory,
                SKOS.Concept,
                category_uri,
                health_category.value.eng_label,
            )

    def _add_health_themes(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        for health_theme in dataset.health_themes:
            # Construct full URI instead of using just the key
            theme_uri = f"{HEALTH_VOCABULARY_BASE}healththemes/{health_theme.key}"
            self.graph_builder.add_uri_resource_with_label(
                dataset_uri,
                HEALTHDCATAP.healthTheme,
                SKOS.Concept,
                theme_uri,
                health_theme.value.eng_label,
            )

    def _add_typical_age(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.min_typical_age is not None:
            self.graph.add(
                (
                    dataset_uri,
                    HEALTHDCATAP.minTypicalAge,
                    Literal(
                        datatype=XSD.nonNegativeInteger,
                        lexical_or_value=dataset.min_typical_age,
                    ),
                )
            )

        if dataset.max_typical_age is not None:
            self.graph.add(
                (
                    dataset_uri,
                    HEALTHDCATAP.maxTypicalAge,
                    Literal(
                        datatype=XSD.nonNegativeInteger,
                        lexical_or_value=dataset.max_typical_age,
                    ),
                )
            )

    def _add_number_of_records(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.number_of_records is not None:
            self.graph.add(
                (
                    dataset_uri,
                    HEALTHDCATAP.numberOfRecords,
                    Literal(
                        datatype=XSD.nonNegativeInteger,
                        lexical_or_value=dataset.number_of_records,
                    ),
                )
            )

    def _add_number_of_unique_individuals(
        self, dataset_uri: URIRef, dataset: Dataset
    ) -> None:
        if dataset.number_of_unique_individuals is not None:
            self.graph.add(
                (
                    dataset_uri,
                    HEALTHDCATAP.numberOfUniqueIndividuals,
                    Literal(
                        datatype=XSD.nonNegativeInteger,
                        lexical_or_value=dataset.number_of_unique_individuals,
                    ),
                )
            )

    def _add_population_coverage(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.population_coverage is not None:
            self.graph.add(
                (
                    dataset_uri,
                    HEALTHDCATAP.populationCoverage,
                    Literal(lang="eng", lexical_or_value=dataset.population_coverage),
                ),
            )

    def _add_code_values(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if not dataset.code_values:
            return

        for code_value in dataset.code_values:
            self.graph.add(
                (
                    dataset_uri,
                    HEALTHDCATAP.hasCodeValues,
                    Literal(lang="eng", lexical_or_value=code_value.value),
                ),
            )

    def _add_purpose(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.purpose_entries:
            for purpose_entry in dataset.purpose_entries:
                purpose_node = BNode()
                self.graph.add((dataset_uri, DPV.hasPurpose, purpose_node))
                self.graph.add((purpose_node, RDF.type, DPV.Purpose))
                self.graph.add(
                    (
                        purpose_node,
                        DCTERMS.description,
                        Literal(lang="eng", lexical_or_value=purpose_entry.value),
                    )
                )

    def _add_coding_systems(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.coding_systems:
            for coding_system in dataset.coding_systems:
                coding_system_uri = URIRef(coding_system.value)
                self.graph.add(
                    (dataset_uri, HEALTHDCATAP.hasCodingSystem, coding_system_uri)
                )
                self.graph.add((coding_system_uri, RDF.type, DCTERMS.Standard))

    def _add_health_data_access_body(
        self, dataset_uri: URIRef, dataset: Dataset
    ) -> None:
        if not dataset.health_categories:
            return

        hdab_config = self.graph_builder.get_health_data_access_body_config()
        if not hdab_config:
            return

        hdab_uri = URIRef(hdab_config["identifier"])
        self.graph.add((hdab_uri, RDF.type, FOAF.Agent))
        self.graph.add((hdab_uri, RDF.type, FOAF.Organization))
        self.graph.add((hdab_uri, FOAF.name, Literal(hdab_config["name"], lang="eng")))

        contact_node = BNode()
        self.graph.add((hdab_uri, DCAT.contactPoint, contact_node))
        self.graph.add((contact_node, RDF.type, VCARD.Kind))
        self.graph.add((contact_node, VCARD.fn, Literal(hdab_config["contact_name"])))
        self.graph.add(
            (
                contact_node,
                VCARD.hasEmail,
                URIRef(f"mailto:{hdab_config['contact_email']}"),
            )
        )

        self.graph.add((dataset_uri, HEALTHDCATAP.hdab, hdab_uri))

    def _add_qualified_attributions(
        self, dataset_uri: URIRef, dataset: Dataset
    ) -> None:
        for qualified_attribution in dataset.qualified_attributions:
            organisation = qualified_attribution.organisation
            if organisation:
                attribution_node = BNode()

                self.graph.add(
                    (dataset_uri, PROV.qualifiedAttribution, attribution_node)
                )
                self.graph.add((attribution_node, RDF.type, PROV.Attribution))

                # Use blank node for agent (consistent with publisher pattern)
                agent_node = BNode()
                self.graph.add((attribution_node, PROV.agent, agent_node))
                self.graph.add((agent_node, RDF.type, FOAF.Agent))
                self.graph.add((agent_node, RDF.type, FOAF.Organization))
                self.graph.add(
                    (agent_node, FOAF.name, Literal(organisation.name, lang="eng"))
                )

                if qualified_attribution.role:
                    role_uri = self._get_inspire_role_uri(qualified_attribution.role)
                    self.graph.add((attribution_node, DCAT.hadRole, role_uri))
                    # Add type declaration for DCAT-AP compliance
                    self.graph.add((role_uri, RDF.type, DCAT.Role))
                    # Add human-readable label for the role
                    role_label = qualified_attribution.role.replace("_", " ").title()
                    self.graph.add(
                        (role_uri, SKOS.prefLabel, Literal(role_label, lang="eng"))
                    )

    def _get_inspire_role_uri(self, role: str) -> URIRef:
        normalized_role = role.lower().replace(" ", "").replace("_", "")

        return URIRef(
            f"http://inspire.ec.europa.eu/metadata-codelist/ResponsiblePartyRole/{normalized_role}"  # NOSONAR
        )

    def _add_spatial_coverage(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.spatial_coverages:
            for spatial_coverage in dataset.spatial_coverages:
                self.graph_builder.add_uri_resource_with_label(
                    dataset_uri,
                    DCTERMS.spatial,
                    DCTERMS.Location,
                    spatial_coverage.key,
                    spatial_coverage.value.eng_label,
                )

    def _add_legal_information(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        # Applicable legislation
        if dataset.applicable_legislations:
            applicable_legislations = self.applicable_legislation_repository.get_all()
            for legislation in dataset.applicable_legislations:
                self.graph_builder.add_legal_resource(
                    dataset_uri,
                    legislation,
                    applicable_legislations,
                    lambda x, key: x.eng_label if x.key == key else None,
                )

    def _add_dataset_types(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        for dataset_type in dataset.dataset_types:
            self.graph_builder.add_uri_resource_with_label(
                dataset_uri,
                DCTERMS.type,
                SKOS.Concept,
                dataset_type.key,
                dataset_type.value.eng_label,
            )

    def _add_temporal_information(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.modified_at:
            self.graph.add(
                (
                    dataset_uri,
                    DCTERMS.modified,
                    Literal(
                        datatype=XSD.dateTime,
                        lexical_or_value=dataset.modified_at.isoformat(),
                    ),
                )
            )

        if dataset.release_date:
            self.graph.add(
                (
                    dataset_uri,
                    DCTERMS.issued,
                    Literal(
                        datatype=XSD.dateTime,
                        lexical_or_value=dataset.release_date.isoformat(),
                    ),
                )
            )

        if dataset.version:
            self.graph.add(
                (
                    dataset_uri,
                    DCAT.version,
                    Literal(lexical_or_value=dataset.version),
                )
            )

        if dataset.version_notes:
            for version_note in dataset.version_notes:
                self.graph.add(
                    (
                        dataset_uri,
                        ADMS.versionNotes,
                        Literal(lexical_or_value=version_note.value),
                    )
                )

    def _add_creator(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.creators:
            for dataset_creator in dataset.creators:
                creator = BNode()
                self.graph.add((creator, RDF.type, FOAF.Agent))
                self.graph.add((creator, RDF.type, FOAF.Organization))
                self.graph.add(
                    (
                        creator,
                        FOAF.name,
                        Literal(
                            lang="eng",
                            lexical_or_value=dataset_creator.organisation.name,
                        ),
                    )
                )
                self.graph.add((dataset_uri, DCTERMS.creator, creator))

    def _add_provenance(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.provenance_entries:
            for provenance_entry in dataset.provenance_entries:
                provenance_node = BNode()
                self.graph.add((provenance_node, RDF.type, DCTERMS.ProvenanceStatement))
                self.graph.add(
                    (
                        provenance_node,
                        RDFS.label,
                        Literal(provenance_entry.value, lang="eng"),
                    )
                )
                self.graph.add((dataset_uri, DCTERMS.provenance, provenance_node))

    def _add_health_legal_basis(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.health_legal_basis_entries:
            for entry in dataset.health_legal_basis_entries:
                legal_basis_node = BNode()
                self.graph.add((legal_basis_node, RDF.type, DPV.LegalBasis))
                self.graph.add(
                    (
                        legal_basis_node,
                        DCTERMS.description,
                        Literal(entry.value, lang="eng"),
                    )
                )
                self.graph.add((dataset_uri, DPV.hasLegalBasis, legal_basis_node))

    def _add_languages(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.languages:
            for language in dataset.languages:
                self.graph_builder.add_language(dataset_uri, language.key)

    def _add_other_properties(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.landing_pages:
            for landing_page in dataset.landing_pages:
                self.graph_builder.add_document(
                    dataset_uri, DCAT.landingPage, landing_page.url
                )

        for protection_type in dataset.data_protection_types:
            label = self.graph_builder.convert_camelcase_to_label(protection_type.key)
            self.graph.add(
                (
                    dataset_uri,
                    DPV.dataProtectionType,
                    Literal(lang="eng", lexical_or_value=label),
                )
            )

        for conforms_to_value in dataset.conforms_to_values:
            standard_uri = URIRef(conforms_to_value.key)
            self.graph.add((dataset_uri, DCTERMS.conformsTo, standard_uri))
            self.graph.add((standard_uri, RDF.type, DCTERMS.Standard))

        for identifier in dataset.other_identifiers:
            identifier_node = BNode()
            self.graph.add((dataset_uri, ADMS.identifier, identifier_node))
            self.graph.add((identifier_node, RDF.type, ADMS.Identifier))
            self.graph.add((identifier_node, SKOS.notation, Literal(identifier.key)))

        for was_generated_by in dataset.was_generated_by:
            activity_node = BNode()
            self.graph.add((dataset_uri, PROV.wasGeneratedBy, activity_node))
            self.graph.add((activity_node, RDF.type, PROV.Activity))
            self.graph.add(
                (
                    activity_node,
                    RDFS.label,
                    Literal(was_generated_by.key, lang="eng"),
                )
            )

        for sr in dataset.spatial_resolutions:
            self.graph.add(
                (
                    dataset_uri,
                    DCAT.spatialResolutionInMeters,
                    Literal(
                        datatype=XSD.decimal,
                        lexical_or_value=sr.value,
                    ),
                )
            )

        if dataset.temporal_resolution:
            self.graph.add(
                (
                    dataset_uri,
                    DCAT.temporalResolution,
                    Literal(
                        datatype=XSD.duration,
                        lexical_or_value=dataset.temporal_resolution,
                    ),
                )
            )

        if dataset.documentation_entries:
            for doc_entry in dataset.documentation_entries:
                self.graph_builder.add_document(dataset_uri, FOAF.page, doc_entry.value)

    def _add_publisher_and_contact(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        publisher = BNode()
        self.graph.add((dataset_uri, DCTERMS.publisher, publisher))
        self.graph.add((publisher, RDF.type, FOAF.Agent))
        self.graph.add((publisher, RDF.type, FOAF.Organization))
        self.graph.add(
            (
                publisher,
                FOAF.name,
                Literal(lang="eng", lexical_or_value=dataset.publisher.name),
            )
        )

        # Publisher type
        if dataset.publisher.type:
            adms_type = TypeMappers.map_org_type(dataset.publisher.type)
            label = re.sub(r"(?<!^)(?=[A-Z])", " ", adms_type)
            adms_type_uri = f"http://purl.org/adms/publishertype/{adms_type}"
            self.graph_builder.add_uri_resource_with_label(
                publisher, DCTERMS.type, SKOS.Concept, adms_type_uri, label
            )

        # Publisher email
        if dataset.publisher.email:
            self.graph.add(
                (publisher, FOAF.mbox, URIRef(f"mailto:{dataset.publisher.email}"))
            )

        # Contact Points - DCAT-AP compliant
        if dataset.contacts:
            for dataset_contact in dataset.contacts:
                if dataset_contact.contact:
                    contact_point = BNode()
                    self.graph.add((dataset_uri, DCAT.contactPoint, contact_point))
                    self.graph.add((contact_point, RDF.type, VCARD.Individual))
                    self.graph.add(
                        (
                            contact_point,
                            VCARD.fn,
                            Literal(
                                lang="eng",
                                lexical_or_value=dataset_contact.contact.name,
                            ),
                        )
                    )
                    self.graph.add(
                        (
                            contact_point,
                            VCARD.hasEmail,
                            URIRef(f"mailto:{dataset_contact.contact.email}"),
                        )
                    )
                    if dataset_contact.contact.role:
                        self.graph.add(
                            (
                                contact_point,
                                VCARD.role,
                                Literal(
                                    lang="eng",
                                    lexical_or_value=dataset_contact.contact.role,
                                ),
                            )
                        )
                    # DCAT-AP requires contact points to be vcard:Kind or subclass; add explicit Kind typing
                    self.graph.add((contact_point, RDF.type, VCARD.Kind))
        else:
            contact_point = BNode()
            self.graph.add((dataset_uri, DCAT.contactPoint, contact_point))
            self.graph.add((contact_point, RDF.type, VCARD.Organization))
            self.graph.add(
                (
                    contact_point,
                    VCARD.fn,
                    Literal(lang="eng", lexical_or_value=dataset.publisher.name),
                )
            )
            if dataset.publisher.email:
                self.graph.add(
                    (
                        contact_point,
                        VCARD.hasEmail,
                        URIRef(f"mailto:{dataset.publisher.email}"),
                    )
                )
            # DCAT-AP requires contact points to be vcard:Kind or subclass; add explicit Kind typing
            self.graph.add((contact_point, RDF.type, VCARD.Kind))

    def _add_temporal_period(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if not dataset.time_period_start and not dataset.time_period_end:
            return

        temporal = BNode()
        self.graph.add((temporal, RDF.type, DCTERMS.PeriodOfTime))

        # Start date (if available)
        if dataset.time_period_start:
            self.graph.add(
                (
                    temporal,
                    DCAT.startDate,
                    Literal(
                        datatype=XSD.date,
                        lexical_or_value=dataset.time_period_start.isoformat(),
                    ),
                )
            )

        # End date (if available)
        if dataset.time_period_end:
            self.graph.add(
                (
                    temporal,
                    DCAT.endDate,
                    Literal(
                        datatype=XSD.date,
                        lexical_or_value=dataset.time_period_end.isoformat(),
                    ),
                )
            )

        self.graph.add(
            (temporal, DCTERMS.title, Literal("Dataset Coverage Period", lang="eng"))
        )
        self.graph.add((dataset_uri, DCTERMS.temporal, temporal))

    def _add_retention_period(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        # Only add retention period if at least one of the dates is present
        if not dataset.retention_period_start and not dataset.retention_period_end:
            return

        retention = BNode()
        self.graph.add((retention, RDF.type, DCTERMS.PeriodOfTime))

        # Start date (if available)
        if dataset.retention_period_start:
            self.graph.add(
                (
                    retention,
                    DCAT.startDate,
                    Literal(
                        datatype=XSD.date,
                        lexical_or_value=dataset.retention_period_start.isoformat(),
                    ),
                )
            )

        # End date (if available)
        if dataset.retention_period_end:
            self.graph.add(
                (
                    retention,
                    DCAT.endDate,
                    Literal(
                        datatype=XSD.date,
                        lexical_or_value=dataset.retention_period_end.isoformat(),
                    ),
                )
            )

        # Use Health DCAT-AP namespace for retention period
        self.graph.add((dataset_uri, HEALTHDCATAP.retentionPeriod, retention))

    def _add_relations(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        for relation in dataset.source_relations:
            if relation.is_dataset_relation:
                self._add_dataset_relation(dataset_uri, relation)
            elif relation.is_external_relation:
                self._add_external_relation(dataset_uri, relation)

    def _add_dataset_relation(
        self, dataset_uri: URIRef, relation: "DatasetRelationEntry"
    ) -> None:
        target_dataset_uri = self.graph_builder.get_dataset_uri(
            relation.target.identifier
        )
        if ":" in relation.relation_type:
            relation_type = relation.relation_type.split(":")[1]
        else:
            relation_type = relation.relation_type
        if hasattr(DCTERMS, relation_type):
            self.graph.add((dataset_uri, DCTERMS[relation_type], target_dataset_uri))
        else:
            self.graph.add((dataset_uri, DCTERMS.relation, target_dataset_uri))

    def _add_external_relation(self, dataset_uri: URIRef, relation) -> None:
        external_resource_uri = URIRef(relation.external_url)

        if relation.external_role == "is-referenced-by":
            self.graph.add((dataset_uri, DCTERMS.isReferencedBy, external_resource_uri))
            return

        relation_node = BNode()
        self.graph.add((dataset_uri, DCAT.qualifiedRelation, relation_node))
        self.graph.add((relation_node, RDF.type, DCAT.Relationship))

        self.graph.add((relation_node, DCTERMS.relation, external_resource_uri))
        # Add type declaration and required properties for DCAT-AP compliance
        self.graph.add((external_resource_uri, RDF.type, DCAT.Resource))
        # Add required title for DcatResource_Shape
        title = (
            relation.external_description
            if relation.external_description
            else relation.external_url
        )
        self.graph.add(
            (external_resource_uri, DCTERMS.title, Literal(title, lang="eng"))
        )

        if relation.external_role:
            role_normalized = self._normalize_role_token(relation.external_role)
            role_uri = URIRef(
                f"http://www.iana.org/assignments/relation/{role_normalized}"
            )
            self.graph.add((relation_node, DCAT.hadRole, role_uri))
            # Add type declaration for DCAT-AP compliance
            self.graph.add((role_uri, RDF.type, DCAT.Role))
            # Add label for the role
            self.graph.add(
                (role_uri, SKOS.prefLabel, Literal(relation.external_role, lang="eng"))
            )

        if relation.external_description:
            self.graph.add(
                (
                    relation_node,
                    RDFS.label,
                    Literal(relation.external_description, lang="eng"),
                )
            )

    def _normalize_role_token(self, token: str) -> str:
        if not token:
            return ""
        return token.strip().replace(" ", "-").replace("_", "-").lower()

    def _add_data_dictionary(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        # Get data dictionary entries with correct ordering from repository
        entries = self.data_dictionary_repository.get_data_dictionaries_by_dataset_id(
            dataset.id
        )

        if entries:
            dictionary_node = BNode()
            self.graph.add((dataset_uri, FOAF.page, dictionary_node))
            self.graph.add((dictionary_node, RDF.type, FOAF.Document))
            self.graph.add((dictionary_node, RDF.type, CSVW.TableSchema))

            for entry in entries:
                entry_node = BNode()
                # Treat each data dictionary entry as a CSVW column definition
                self.graph.add((entry_node, RDF.type, CSVW.Column))
                self.graph.add((dictionary_node, CSVW.column, entry_node))
                self.graph.add((entry_node, CSVW.name, Literal(entry.field_name)))

                # Map data type to XSD
                xsd_type = TypeMappers.map_dca_to_xsd_type(entry.data_type)
                self.graph.add((entry_node, CSVW.datatype, xsd_type))

                if entry.description:
                    self.graph.add(
                        (
                            entry_node,
                            DCTERMS.description,
                            Literal(entry.description, lang="eng"),
                        )
                    )

                if entry.personally_identifiable_variable:
                    self.graph.add((entry_node, RDF.type, DPV.PersonalData))

                if entry.required is not None:
                    self.graph.add(
                        (
                            entry_node,
                            CSVW.required,
                            Literal(entry.required, datatype=XSD.boolean),
                        )
                    )

                if entry.max_allowed_value is not None:
                    self.graph.add(
                        (
                            entry_node,
                            CSVW.maxInclusive,
                            Literal(entry.max_allowed_value, datatype=XSD.decimal),
                        )
                    )

                if entry.min_allowed_value is not None:
                    self.graph.add(
                        (
                            entry_node,
                            CSVW.minInclusive,
                            Literal(entry.min_allowed_value, datatype=XSD.decimal),
                        )
                    )

                if entry.variable_unit:
                    self.graph.add(
                        (
                            entry_node,
                            CSVW.unit,
                            Literal(entry.variable_unit),
                        )
                    )

                if entry.allowed_values:
                    self.graph.add(
                        (
                            entry_node,
                            CSVW["in"],
                            Literal(entry.allowed_values, lang="eng"),
                        )
                    )

                if entry.allowed_values_description:
                    self.graph.add(
                        (
                            entry_node,
                            RDFS.comment,
                            Literal(entry.allowed_values_description, lang="eng"),
                        )
                    )

                if entry.privacy_risk_type:
                    self.graph.add(
                        (
                            entry_node,
                            CDSP.privacyRiskType,
                            Literal(entry.privacy_risk_type, lang="eng"),
                        )
                    )

    def _add_dataset_series_info(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.is_dataset_series and dataset.member_datasets:
            sorted_members = sorted(dataset.member_datasets, key=lambda m: m.position)

            # First member
            first_member = next((m for m in sorted_members if m.is_first), None)
            if first_member:
                first_uri = self.graph_builder.get_dataset_uri(
                    first_member.dataset.identifier
                )
                self.graph.add((dataset_uri, DCAT.first, first_uri))

            # Last member
            last_member = next((m for m in sorted_members if m.is_last), None)
            if last_member:
                last_uri = self.graph_builder.get_dataset_uri(
                    last_member.dataset.identifier
                )
                self.graph.add((dataset_uri, DCAT.last, last_uri))

            # Navigation chain
            for i in range(len(sorted_members) - 1):
                current_member = sorted_members[i]
                next_member = sorted_members[i + 1]

                current_uri = self.graph_builder.get_dataset_uri(
                    current_member.dataset.identifier
                )
                next_uri = self.graph_builder.get_dataset_uri(
                    next_member.dataset.identifier
                )

                self.graph.add((current_uri, DCAT.next, next_uri))
                self.graph.add((next_uri, DCAT.prev, current_uri))

        # Series memberships
        if dataset.series_memberships:
            for membership in dataset.series_memberships:
                series_uri = self.graph_builder.get_dataset_uri(
                    membership.series.identifier
                )
                self.graph.add((dataset_uri, DCAT.inSeries, series_uri))

    def _add_keywords(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if not dataset.keywords:
            return
        for keyword in dataset.keywords:
            self.graph.add(
                (
                    dataset_uri,
                    DCAT.keyword,
                    Literal(
                        lang="eng",
                        lexical_or_value=getattr(keyword.value, "eng_label", None)
                        or keyword.key,
                    ),
                )
            )

    def _add_personal_data(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if not dataset.personal_data:
            return
        for personal_data in dataset.personal_data:
            self.graph.add(
                (
                    dataset_uri,
                    DPV.hasPersonalData,
                    DPVPD[personal_data.key],
                )
            )

    def _add_authentic_sources(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        # Get data dictionary entries with correct ordering from repository
        entries = self.data_dictionary_repository.get_data_dictionaries_by_dataset_id(
            dataset.id
        )

        for entry in entries:
            if entry.is_authentic_source:
                for assignment in entry.authentic_source_assignments:
                    if assignment.is_active:
                        auth_node = BNode()
                        self.graph.add(
                            (dataset_uri, CDSP.hasAuthenticSource, auth_node)
                        )
                        self.graph.add(
                            (auth_node, CDSP.entryName, Literal(entry.field_name))
                        )
                        self.graph.add(
                            (
                                auth_node,
                                CDSP.entryDescription,
                                Literal(entry.description, lang="eng"),
                            )
                        )
                        self.graph.add(
                            (
                                auth_node,
                                CDSP.labelName,
                                Literal(assignment.label.name, lang="eng"),
                            )
                        )
                        if assignment.label.description:
                            self.graph.add(
                                (
                                    auth_node,
                                    CDSP.labelDescription,
                                    Literal(assignment.label.description, lang="eng"),
                                )
                            )

    def _add_status(self, dataset_uri: URIRef, dataset: Dataset) -> None:
        if dataset.status:
            # Map internal status to Front Office status
            fo_status = self._map_to_front_office_status(dataset)
            self.graph.add((dataset_uri, CDSP.status, Literal(fo_status)))

    def _map_to_front_office_status(self, dataset: Dataset) -> str:
        if dataset.status == DatasetStatus.PUBLISHED.value:
            return "PUBLISHED"
        elif dataset.status == DatasetStatus.DEPRECATED.value:
            return "DEPRECATED"
        elif (
            dataset.status == DatasetStatus.APPROVED.value
            and dataset.released_at is not None
        ):
            # Was published before (has released_at), now moved back to APPROVED = unpublished
            return "WITHDRAWN"
        else:
            # Default to current status (DRAFT, COMPLETED, VALIDATED, etc.)
            return dataset.status
