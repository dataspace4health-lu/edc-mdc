from rdflib import Graph
from rdflib.namespace import DCAT, RDF
from models.organisation import Organisation
from repositories.organisation import OrganisationRepository
from services.catalogues.importers.qualified_attribution_rdf_mapper import (
    QualifiedAttributionRDFMapper,
)

SAMPLE_QUALIFIED_ATTRIBUTION_RDF = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

<http://example.org/datasets/1>
    a dcat:Dataset ;
    dct:title "Test Dataset"@eng ;
    prov:qualifiedAttribution [
        a prov:Attribution ;
        prov:agent [
            a foaf:Agent, foaf:Organization ;
            foaf:name "Data Analytics Team"@eng
        ] ;
        dcat:hadRole <http://inspire.ec.europa.eu/metadata-codelist/ResponsiblePartyRole/pointofcontact>
    ] ;
    prov:qualifiedAttribution [
        a prov:Attribution ;
        prov:agent [
            a foaf:Agent, foaf:Organization ;
            foaf:name "Research Department"@eng
        ] ;
        dcat:hadRole <http://inspire.ec.europa.eu/metadata-codelist/ResponsiblePartyRole/originator>
    ] ;
    prov:qualifiedAttribution [
        a prov:Attribution ;
        prov:agent [
            a foaf:Agent, foaf:Organization ;
            foaf:name "Data Custodian Unit"@eng
        ] ;
        dcat:hadRole <http://inspire.ec.europa.eu/metadata-codelist/ResponsiblePartyRole/custodian>
    ] .
""".strip()


SAMPLE_MULTIPLE_ROLES_RDF = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

<http://example.org/datasets/2>
    a dcat:Dataset ;
    dct:title "Test Dataset 2"@eng ;
    prov:qualifiedAttribution [
        a prov:Attribution ;
        prov:agent [
            a foaf:Agent, foaf:Organization ;
            foaf:name "Quality Assurance"@eng
        ] ;
        dcat:hadRole <http://inspire.ec.europa.eu/metadata-codelist/ResponsiblePartyRole/principalinvestigator>
    ] ;
    prov:qualifiedAttribution [
        a prov:Attribution ;
        prov:agent [
            a foaf:Agent, foaf:Organization ;
            foaf:name "Distribution Center"@eng
        ] ;
        dcat:hadRole <http://inspire.ec.europa.eu/metadata-codelist/ResponsiblePartyRole/resourceprovider>
    ] .
""".strip()


def _prepare_dependencies(db_session):
    organisations = [
        ("Data Analytics Team", "team", "analytics@example.org"),
        ("Research Department", "department", "research@example.org"),
        ("Data Custodian Unit", "unit", "custodian@example.org"),
        ("Quality Assurance", "department", "qa@example.org"),
        ("Distribution Center", "center", "distribution@example.org"),
    ]

    for name, org_type, email in organisations:
        existing = (
            db_session.query(Organisation).filter(Organisation.name == name).first()
        )
        if existing is None:
            organisation = Organisation(name=name, type=org_type, email=email)
            db_session.add(organisation)

    db_session.commit()

    organisation_repo = OrganisationRepository(db_session)
    return organisation_repo


def test_map_qualified_attributions_basic_roles(db_session):
    organisation_repo = _prepare_dependencies(db_session)
    mapper = QualifiedAttributionRDFMapper(organisation_repository=organisation_repo)

    graph = Graph()
    graph.parse(data=SAMPLE_QUALIFIED_ATTRIBUTION_RDF, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    attributions = mapper.map_qualified_attributions(graph, dataset_uri)

    assert len(attributions) == 3

    # Check that organisations were found
    org_names = {
        organisation_repo.get_organisation(attr.organisation_id).name
        for attr in attributions
    }
    assert org_names == {
        "Data Analytics Team",
        "Research Department",
        "Data Custodian Unit",
    }

    # Check roles are correctly mapped from INSPIRE URI format to DB format
    roles = {attr.role for attr in attributions}
    assert roles == {"pointOfContact", "originator", "custodian"}


def test_map_qualified_attributions_camelcase_roles(db_session):
    organisation_repo = _prepare_dependencies(db_session)
    mapper = QualifiedAttributionRDFMapper(organisation_repository=organisation_repo)

    from rdflib import Graph

    graph = Graph()
    graph.parse(data=SAMPLE_MULTIPLE_ROLES_RDF, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    attributions = mapper.map_qualified_attributions(graph, dataset_uri)

    assert len(attributions) == 2

    # Check camelCase role conversion
    roles = {attr.role for attr in attributions}
    assert roles == {"principalInvestigator", "resourceProvider"}
