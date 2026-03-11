from datetime import date

from models.applicable_legislation import ApplicableLegislation
from repositories.applicable_legislation import ApplicableLegislationRepository
from services.catalogues.importers.distribution_rdf_mapper import (
    DistributionRDFMapper,
)
from rdflib.namespace import DCAT, RDF
from rdflib import Graph

SAMPLE_DISTRIBUTION_RDF = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix spdx: <http://spdx.org/rdf/terms#> .
@prefix r5r: <http://data.europa.eu/r5r/> .
@prefix adms: <http://www.w3.org/ns/adms#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .

<http://example.org/datasets/1>
    a dcat:Dataset ;
    dct:title "Test Dataset"@eng ;
    dcat:distribution [
        a dcat:Distribution ;
        dct:identifier "1" ;
        dct:title "CSV Distribution"@eng ;
        dct:description "A sample CSV distribution of the dataset"@eng ;
        dct:rights <http://publications.europa.eu/resource/authority/access-right/PUBLIC> ;
        dct:format <http://publications.europa.eu/resource/authority/file-type/CSV> ;
        dcat:mediaType <http://www.iana.org/assignments/media-types/text/csv> ;
        dcat:compressFormat <http://www.iana.org/assignments/media-types/application/gzip> ;
        dcat:packageFormat <http://www.iana.org/assignments/media-types/application/zip> ;
        dcat:downloadURL <https://example.org/data.csv> ;
        dcat:accessURL <https://example.org/data> ;
        dct:language <http://publications.europa.eu/resource/authority/language/ENG> ;
        dct:license <http://spdx.org/licenses/MIT> ;
        dct:issued "2024-01-15T00:00:00"^^xsd:dateTime ;
        dct:modified "2024-02-20T00:00:00"^^xsd:dateTime ;
        r5r:availability <http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE> ;
        r5r:applicableLegislation <http://example.org/legal/basis> ;
        dcat:byteSize "1024"^^xsd:nonNegativeInteger ;
        dcat:spatialResolutionInMeters "100"^^xsd:decimal ;
        dcat:temporalResolution "P1D"^^xsd:duration ;
        adms:status <http://publications.europa.eu/resource/authority/distribution-status/COMPLETED> ;
        foaf:page <https://example.org/docs> ;
        dct:conformsTo <https://example.org/schema/v1> ;
        spdx:checksum [
            a spdx:Checksum ;
            spdx:algorithm spdx:checksumAlgorithm_sha1 ;
            spdx:checksumValue "abc123def456"^^xsd:hexBinary
        ] ;
        odrl:hasPolicy [
            a odrl:Policy, odrl:Set ;
            odrl:permission [
                a odrl:Permission ;
                odrl:action odrl:use ;
                odrl:constraint [
                    odrl:leftOperand odrl:dateTime ;
                    odrl:operator odrl:gteq ;
                    odrl:rightOperand "2024-01-01"^^xsd:date
                ] ;
                odrl:constraint [
                    odrl:leftOperand odrl:dateTime ;
                    odrl:operator odrl:lteq ;
                    odrl:rightOperand "2024-12-31"^^xsd:date
                ]
            ]
        ]
    ] .
""".strip()


def _prepare_dependencies(db_session):
    applicable_legislation = db_session.get(
        ApplicableLegislation, "http://example.org/legal/basis"
    )
    if applicable_legislation is None:
        applicable_legislation = ApplicableLegislation(
            key="http://example.org/legal/basis",
            eng_label="Basis",
            description="Legal basis description",
            link="https://example.org/legal/basis",
        )
        db_session.add(applicable_legislation)

    db_session.commit()

    applicable_legislation_repo = ApplicableLegislationRepository(db_session)
    return applicable_legislation_repo


def test_map_distribution_basic_fields(db_session):
    applicable_legislation_repo = _prepare_dependencies(db_session)
    mapper = DistributionRDFMapper(
        applicable_legislation_repository=applicable_legislation_repo,
    )

    graph = Graph()
    graph.parse(data=SAMPLE_DISTRIBUTION_RDF, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    distributions = mapper.map_distributions(graph, dataset_uri)

    assert len(distributions) == 1
    dist = list(distributions)[0]

    assert dist.title == "CSV Distribution"
    assert dist.description == "A sample CSV distribution of the dataset"
    assert (
        dist.rights_statement
        == "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    assert (
        dist.file_type
        == "http://publications.europa.eu/resource/authority/file-type/CSV"
    )
    assert dist.media_type == "text/csv"
    assert dist.compression_format == "application/gzip"
    assert dist.packaging_format == "application/zip"
    assert [str(u) for u in dist.download_urls] == ["https://example.org/data.csv"]
    assert [str(u) for u in dist.access_urls] == ["https://example.org/data"]
    assert dist.languages == frozenset(
        {"http://publications.europa.eu/resource/authority/language/ENG"}
    )
    assert dist.license == "MIT"
    assert dist.release_date == date(2024, 1, 15)
    assert dist.modification_date == date(2024, 2, 20)
    assert (
        dist.availability
        == "http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE"
    )
    assert dist.applicable_legislations == frozenset({"http://example.org/legal/basis"})
    assert dist.byte_size == 1024
    assert dist.spatial_resolution == 100
    assert dist.temporal_resolution == "P1D"
    assert dist.distribution_dcat_status == "Completed"
    assert len(dist.documentation) == 1
    assert str(dist.documentation[0]) == "https://example.org/docs"
    assert dist.linked_schemas == ["https://example.org/schema/v1"]
    assert dist.checksum == "abc123def456"
    assert dist.internal_only is False
    assert dist.is_analytics is False


def test_map_distribution_policy_actions(db_session):
    applicable_legislation_repo = _prepare_dependencies(db_session)
    mapper = DistributionRDFMapper(
        applicable_legislation_repository=applicable_legislation_repo,
    )

    graph = Graph()
    graph.parse(data=SAMPLE_DISTRIBUTION_RDF, format="turtle")

    dataset_uri = list(graph.subjects(RDF.type, DCAT.Dataset))[0]
    distributions = mapper.map_distributions(graph, dataset_uri)

    dist = list(distributions)[0]
    assert len(dist.policy_actions) == 1

    policy = dist.policy_actions[0]
    assert policy.policy_action_type == "permission"
    assert policy.policy_constraint_type == "temporal"
    assert policy.temporal_restriction_start == date(2024, 1, 1)
    assert policy.temporal_restriction_end == date(2024, 12, 31)


def test_skip_sample_distributions(db_session):
    applicable_legislation_repo = _prepare_dependencies(db_session)
    mapper = DistributionRDFMapper(
        applicable_legislation_repository=applicable_legislation_repo,
    )

    sample_rdf = """
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix adms: <http://www.w3.org/ns/adms#> .

    <http://example.org/datasets/1>
        a dcat:Dataset ;
        dct:title "Test Dataset"@eng ;
        adms:sample [
            a dcat:Distribution ;
            dct:title "Sample Distribution"@eng ;
            dct:description "A sample distribution"@eng ;
            dct:rights <https://example.org/rights>
        ] .
    """.strip()

    graph = Graph()
    graph.parse(data=sample_rdf, format="turtle")

    dataset_uri = list(graph.subjects(RDF.type, DCAT.Dataset))[0]
    distributions = mapper.map_distributions(graph, dataset_uri)

    # Sample distributions should be skipped
    assert len(distributions) == 0


def test_map_analytics_distribution(db_session):
    applicable_legislation_repo = _prepare_dependencies(db_session)
    mapper = DistributionRDFMapper(
        applicable_legislation_repository=applicable_legislation_repo,
    )

    analytics_rdf = """
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix healthdcatap: <http://healthdataportal.eu/ns/health#> .

    <http://example.org/datasets/1>
        a dcat:Dataset ;
        dct:title "Test Dataset"@eng ;
        healthdcatap:analytics [
            a dcat:Distribution ;
            dct:title "Analytics Distribution"@eng ;
            dct:description "A technical report distribution"@eng ;
            dct:rights <https://example.org/rights> ;
            dcat:accessURL <https://example.org/analytics>
        ] .
    """.strip()

    graph = Graph()
    graph.parse(data=analytics_rdf, format="turtle")

    dataset_uri = list(graph.subjects(RDF.type, DCAT.Dataset))[0]
    distributions = mapper.map_distributions(graph, dataset_uri)

    assert len(distributions) == 1
    dist = list(distributions)[0]

    assert dist.title == "Analytics Distribution"
    assert dist.is_analytics is True


def test_map_distribution_minimal_required_fields(db_session):
    applicable_legislation_repo = _prepare_dependencies(db_session)
    mapper = DistributionRDFMapper(
        applicable_legislation_repository=applicable_legislation_repo,
    )

    minimal_rdf = """
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .

    <http://example.org/datasets/1>
        a dcat:Dataset ;
        dct:title "Test Dataset"@eng ;
        dcat:distribution [
            a dcat:Distribution ;
            dct:title "Minimal Distribution"@eng ;
            dct:description "A minimal distribution with only required fields"@eng ;
            dct:rights <https://example.org/rights> ;
            dcat:accessURL <https://example.org/access>
        ] .
    """.strip()

    graph = Graph()
    graph.parse(data=minimal_rdf, format="turtle")

    dataset_uri = list(graph.subjects(RDF.type, DCAT.Dataset))[0]
    distributions = mapper.map_distributions(graph, dataset_uri)

    assert len(distributions) == 1
    dist = list(distributions)[0]

    assert dist.title == "Minimal Distribution"
    assert dist.description == "A minimal distribution with only required fields"
    assert dist.rights_statement == "https://example.org/rights"
    assert [str(u) for u in dist.access_urls] == ["https://example.org/access"]
    assert dist.download_urls == []
    assert dist.byte_size is None
