from enum import Enum


class CatalogueFormat(str, Enum):
    TTL = "ttl"
    RDF = "rdf"
    JSONLD = "jsonld"
