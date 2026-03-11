from services.catalogues.importers.data_dictionary_rdf_mapper import (
    DataDictionaryRDFMapper,
)
from rdflib.namespace import DCAT, RDF
from rdflib import Graph

SAMPLE_DATA_DICTIONARY_RDF = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix csvw: <http://www.w3.org/ns/csvw#> .
@prefix dpv: <http://www.w3.org/ns/dpv#> .
@prefix cdsp: <http://mindig_lu.gitlab.io/DCAT-AP-LU/vocab/cdsp/> .

<http://example.org/datasets/1>
    a dcat:Dataset ;
    dct:title "Test Dataset"@eng ;
    foaf:page [
        a foaf:Document, csvw:TableSchema ;
        csvw:column [
            a csvw:Column ;
            csvw:name "user_id" ;
            dct:description "Unique identifier for the user"@eng ;
            csvw:datatype xsd:integer ;
            csvw:required "true"^^xsd:boolean
        ] ;
        csvw:column [
            a csvw:Column ;
            csvw:name "email_address" ;
            dct:description "User email address"@eng ;
            csvw:datatype xsd:string ;
            a dpv:PersonalData ;
            csvw:required "false"^^xsd:boolean ;
            cdsp:privacyRiskType "Direct identifier"@eng
        ] ;
        csvw:column [
            a csvw:Column ;
            csvw:name "age" ;
            dct:description "User age in years"@eng ;
            csvw:datatype xsd:integer ;
            csvw:minInclusive "0"^^xsd:decimal ;
            csvw:maxInclusive "150"^^xsd:decimal ;
            csvw:unit "years"
        ] ;
        csvw:column [
            a csvw:Column ;
            csvw:name "account_status" ;
            dct:description "Current status of the account"@eng ;
            csvw:datatype xsd:string ;
            csvw:in "active, inactive, suspended"@eng ;
            rdfs:comment "Allowed values: active, inactive, suspended"@eng
        ]
    ] .
""".strip()


def test_map_data_dictionaries_comprehensive():
    mapper = DataDictionaryRDFMapper()

    graph = Graph()
    graph.parse(data=SAMPLE_DATA_DICTIONARY_RDF, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    data_dicts = mapper.map_data_dictionaries(graph, dataset_uri)

    assert data_dicts is not None
    assert len(data_dicts) == 4

    # Convert to dict for easier assertion
    entries_by_name = {entry.field_name: entry for entry in data_dicts}

    # Test user_id field
    user_id = entries_by_name["user_id"]
    assert user_id.field_name == "user_id"
    assert user_id.description == "Unique identifier for the user"
    assert user_id.data_type == "Integer"
    assert user_id.required is True
    assert user_id.personally_identifiable_variable is None

    # Test email_address field (personal data)
    email = entries_by_name["email_address"]
    assert email.field_name == "email_address"
    assert email.description == "User email address"
    assert email.data_type == "String"
    assert email.required is False
    assert email.personally_identifiable_variable is True
    assert email.privacy_risk_type == "Direct identifier"

    # Test age field (with min/max values and unit)
    age = entries_by_name["age"]
    assert age.field_name == "age"
    assert age.description == "User age in years"
    assert age.data_type == "Integer"
    assert age.min_allowed_value == 0.0
    assert age.max_allowed_value == 150.0
    assert age.variable_unit == "years"

    # Test account_status field (with allowed values)
    status = entries_by_name["account_status"]
    assert status.field_name == "account_status"
    assert status.description == "Current status of the account"
    assert status.data_type == "String"
    assert status.allowed_values == "active, inactive, suspended"
    assert (
        status.allowed_values_description
        == "Allowed values: active, inactive, suspended"
    )


def test_map_data_dictionaries_no_dictionary():
    mapper = DataDictionaryRDFMapper()

    # RDF without data dictionary
    rdf_without_dict = """
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .

    <http://example.org/datasets/1>
        a dcat:Dataset ;
        dct:title "Test Dataset"@eng .
    """.strip()

    graph = Graph()
    graph.parse(data=rdf_without_dict, format="turtle")

    dataset_uri = next(graph.subjects(RDF.type, DCAT.Dataset))

    data_dicts = mapper.map_data_dictionaries(graph, dataset_uri)

    assert data_dicts is None
