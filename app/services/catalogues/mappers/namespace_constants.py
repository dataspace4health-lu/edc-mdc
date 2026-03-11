from rdflib import Namespace
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, RDFS, XSD, SKOS

# Custom namespaces
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")  # NOSONAR
CSVW = Namespace("http://www.w3.org/ns/csvw#")  # NOSONAR
EU_R5R = Namespace("http://data.europa.eu/r5r/")  # NOSONAR
ELI = Namespace("http://data.europa.eu/eli/ontology#")  # NOSONAR
DPV = Namespace("http://www.w3.org/ns/dpv#")  # NOSONAR
SPDX = Namespace("http://spdx.org/rdf/terms#")  # NOSONAR
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")  # NOSONAR
DUO = Namespace("http://purl.obolibrary.org/obo/")  # NOSONAR
ADMS = Namespace("http://www.w3.org/ns/adms#")  # NOSONAR
PROV = Namespace("http://www.w3.org/ns/prov#")  # NOSONAR
CDSP = Namespace("http://mindig_lu.gitlab.io/DCAT-AP-LU/vocab/cdsp/")  # NOSONAR
HEALTHDCATAP = Namespace("http://healthdataportal.eu/ns/health#")  # NOSONAR
DPVPD = Namespace("https://w3id.org/dpv/dpv-pd#")  # NOSONAR
HEALTH_VOCABULARY_BASE = Namespace(
    "http://13.81.34.152:1101/resource/authority/"
)  # NOSONAR

NAMESPACE_BINDINGS = {
    "dcat": DCAT,
    "dct": DCTERMS,
    "foaf": FOAF,
    "xsd": XSD,
    "vcard": VCARD,
    "csvw": CSVW,
    "r5r": EU_R5R,
    "eli": ELI,
    "dpv": DPV,
    "spdx": SPDX,
    "odrl": ODRL,
    "duo": DUO,
    "adms": ADMS,
    "prov": PROV,
    "skos": SKOS,
    "cdsp": CDSP,
    "healthdcatap": HEALTHDCATAP,
    "dpvpd": DPVPD,
}
