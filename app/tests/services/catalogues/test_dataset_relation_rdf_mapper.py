from rdflib import Graph
from rdflib.namespace import DCAT, DCTERMS, RDF
from models.dataset import Dataset
from repositories.dataset import DatasetRepository
from services.catalogues.importers.dataset_relation_rdf_mapper import (
    DatasetRelationRDFMapper,
)

SAMPLE_DATASET_RELATIONS_RDF = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

<https://data.example.org/api/v1/datasets/source-dataset>
    a dcat:Dataset ;
    dct:title "Source Dataset"@eng ;
    dct:source <https://data.example.org/api/v1/datasets/original-dataset> ;
    dct:hasVersion <https://data.example.org/api/v1/datasets/version-2> ;
    dct:replaces <https://data.example.org/api/v1/datasets/old-dataset> ;
    dcat:qualifiedRelation [
        a dcat:Relationship ;
        dct:relation <https://external.example.org/resource/123> ;
        dcat:hadRole <http://www.iana.org/assignments/relation/related> ;
        rdfs:label "Related external resource"@eng
    ] ;
    dcat:qualifiedRelation [
        a dcat:Relationship ;
        dct:relation <https://api.example.org/external-data> ;
        dcat:hadRole <http://www.iana.org/assignments/relation/derived-from> ;
        rdfs:label "Derived from external API"@eng
    ] .
""".strip()


SAMPLE_MULTIPLE_DATASET_RELATIONS_RDF = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .

<https://data.example.org/api/v1/datasets/main-dataset>
    a dcat:Dataset ;
    dct:title "Main Dataset"@eng ;
    dct:hasPart <https://data.example.org/api/v1/datasets/part-a> ;
    dct:hasPart <https://data.example.org/api/v1/datasets/part-b> ;
    dct:isVersionOf <https://data.example.org/api/v1/datasets/original> ;
    dct:references <https://data.example.org/api/v1/datasets/reference-doc> .
""".strip()


def _prepare_dependencies(db_session):
    # Create test datasets
    datasets = [
        ("original-dataset", "Original Dataset"),
        ("version-2", "Version 2 Dataset"),
        ("old-dataset", "Old Dataset"),
        ("part-a", "Part A Dataset"),
        ("part-b", "Part B Dataset"),
        ("original", "Original Version"),
        ("reference-doc", "Reference Documentation"),
    ]

    for identifier, title in datasets:
        existing = (
            db_session.query(Dataset).filter(Dataset.identifier == identifier).first()
        )
        if existing is None:
            dataset = Dataset(
                identifier=identifier,
                title=title,
                description=f"Description of {title}",
                status="draft",
            )
            db_session.add(dataset)

    db_session.commit()

    dataset_repo = DatasetRepository(db_session)
    return dataset_repo


def test_map_dataset_relations_with_mixed_types(db_session):
    dataset_repo = _prepare_dependencies(db_session)
    mapper = DatasetRelationRDFMapper(dataset_repository=dataset_repo)

    graph = Graph()
    graph.parse(data=SAMPLE_DATASET_RELATIONS_RDF, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    relations = mapper.map_dataset_relations(graph, dataset_uri)

    # Should have 3 dataset-to-dataset relations + 2 external relations
    assert len(relations) == 5

    # Check dataset relations
    dataset_relations = [r for r in relations if r.relation_kind == "dataset"]
    assert len(dataset_relations) == 3

    # Check relation types
    relation_types = {r.relation_type for r in dataset_relations}
    assert "dct:source" in relation_types
    assert "dct:hasVersion" in relation_types
    assert "dct:replaces" in relation_types

    # Check external relations
    external_relations = [r for r in relations if r.relation_kind == "external"]
    assert len(external_relations) == 2

    # Check external URLs
    external_urls = {r.external_url for r in external_relations}
    assert "https://external.example.org/resource/123" in external_urls
    assert "https://api.example.org/external-data" in external_urls

    # Check external roles
    external_roles = {r.external_role for r in external_relations if r.external_role}
    assert "related" in external_roles
    assert "derived from" in external_roles

    # Check external descriptions
    external_descriptions = {
        r.external_description for r in external_relations if r.external_description
    }
    assert "Related external resource" in external_descriptions
    assert "Derived from external API" in external_descriptions


def test_map_dataset_relations_multiple_same_type(db_session):
    dataset_repo = _prepare_dependencies(db_session)
    mapper = DatasetRelationRDFMapper(dataset_repository=dataset_repo)

    graph = Graph()
    graph.parse(data=SAMPLE_MULTIPLE_DATASET_RELATIONS_RDF, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    relations = mapper.map_dataset_relations(graph, dataset_uri)

    assert len(relations) == 4

    # Check multiple hasPart relations
    has_part_relations = [r for r in relations if r.relation_type == "dct:hasPart"]
    assert len(has_part_relations) == 2

    # Verify target datasets
    target_ids = {r.target_dataset for r in has_part_relations}
    part_a = dataset_repo.get_dataset_by_identifier("part-a")
    part_b = dataset_repo.get_dataset_by_identifier("part-b")
    assert part_a.id in target_ids
    assert part_b.id in target_ids


def test_map_dataset_relations_unknown_dataset(db_session):
    dataset_repo = _prepare_dependencies(db_session)
    mapper = DatasetRelationRDFMapper(dataset_repository=dataset_repo)

    rdf_with_unknown = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .

<https://data.example.org/api/v1/datasets/test-dataset>
    a dcat:Dataset ;
    dct:title "Test Dataset"@eng ;
    dct:source <https://data.example.org/api/v1/datasets/unknown-dataset> ;
    dct:hasVersion <https://data.example.org/api/v1/datasets/version-2> .
""".strip()

    graph = Graph()
    graph.parse(data=rdf_with_unknown, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    relations = mapper.map_dataset_relations(graph, dataset_uri)

    # Should only have 1 relation (version-2 exists, unknown-dataset doesn't)
    assert len(relations) == 1
    assert relations[0].relation_type == "dct:hasVersion"


def test_map_dataset_relations_external_only(db_session):
    dataset_repo = _prepare_dependencies(db_session)
    mapper = DatasetRelationRDFMapper(dataset_repository=dataset_repo)

    rdf_external_only = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<https://data.example.org/api/v1/datasets/external-test>
    a dcat:Dataset ;
    dct:title "External Test"@eng ;
    dcat:qualifiedRelation [
        a dcat:Relationship ;
        dct:relation <https://example.com/api> ;
        dcat:hadRole <http://www.iana.org/assignments/relation/documentation> ;
        rdfs:label "API Documentation"@eng
    ] ;
    dcat:qualifiedRelation [
        a dcat:Relationship ;
        dct:relation <https://example.com/schema>
    ] .
""".strip()

    graph = Graph()
    graph.parse(data=rdf_external_only, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    relations = mapper.map_dataset_relations(graph, dataset_uri)

    assert len(relations) == 2
    assert all(r.relation_kind == "external" for r in relations)

    # Check first relation has all fields
    relation_with_role = next(
        r for r in relations if r.external_url == "https://example.com/api"
    )
    assert relation_with_role.external_role == "documentation"
    assert relation_with_role.external_description == "API Documentation"

    # Check second relation has minimal fields
    relation_minimal = next(
        r for r in relations if r.external_url == "https://example.com/schema"
    )
    assert relation_minimal.external_role is None
    assert relation_minimal.external_description is None


def test_map_dataset_relations_no_relations(db_session):
    dataset_repo = _prepare_dependencies(db_session)
    mapper = DatasetRelationRDFMapper(dataset_repository=dataset_repo)

    rdf_without_relations = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .

<https://data.example.org/api/v1/datasets/standalone>
    a dcat:Dataset ;
    dct:title "Standalone Dataset"@eng .
""".strip()

    graph = Graph()
    graph.parse(data=rdf_without_relations, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    relations = mapper.map_dataset_relations(graph, dataset_uri)

    assert len(relations) == 0


def test_map_dataset_relations_all_relation_types(db_session):
    dataset_repo = _prepare_dependencies(db_session)
    mapper = DatasetRelationRDFMapper(dataset_repository=dataset_repo)

    rdf_all_types = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .

<https://data.example.org/api/v1/datasets/comprehensive>
    a dcat:Dataset ;
    dct:title "Comprehensive"@eng ;
    dct:isVersionOf <https://data.example.org/api/v1/datasets/original> ;
    dct:hasPart <https://data.example.org/api/v1/datasets/part-a> ;
    dct:isPartOf <https://data.example.org/api/v1/datasets/part-b> ;
    dct:references <https://data.example.org/api/v1/datasets/reference-doc> ;
    dct:isReferencedBy <https://data.example.org/api/v1/datasets/version-2> ;
    dct:replaces <https://data.example.org/api/v1/datasets/old-dataset> ;
    dct:isReplacedBy <https://data.example.org/api/v1/datasets/original-dataset> .
""".strip()

    graph = Graph()
    graph.parse(data=rdf_all_types, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    relations = mapper.map_dataset_relations(graph, dataset_uri)

    # Should have 7 different relation types
    assert len(relations) == 7

    relation_types = {r.relation_type for r in relations}
    expected_types = {
        "dct:isVersionOf",
        "dct:hasPart",
        "dct:isPartOf",
        "dct:references",
        "dct:isReferencedBy",
        "dct:replaces",
        "dct:isReplacedBy",
    }
    assert relation_types == expected_types


def test_map_is_referenced_by_external_resource(db_session):
    dataset_repo = _prepare_dependencies(db_session)
    mapper = DatasetRelationRDFMapper(dataset_repository=dataset_repo)

    rdf = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .

<https://data.example.org/api/v1/datasets/test-dataset>
    a dcat:Dataset ;
    dct:title "Test"@eng ;
    dct:isReferencedBy <https://example.com/publication/42> .
""".strip()

    graph = Graph()
    graph.parse(data=rdf, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    relations = mapper.map_dataset_relations(graph, dataset_uri)

    assert len(relations) == 1
    rel = relations[0]
    assert rel.relation_kind == "external"
    assert rel.external_url == "https://example.com/publication/42"
    assert rel.external_role == "is-referenced-by"
