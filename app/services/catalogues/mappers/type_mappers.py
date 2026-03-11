from rdflib import URIRef
from rdflib.namespace import XSD
from schemas.catalogue import CatalogueFormat


class TypeMappers:
    # Organization type mapping
    ORG_TYPE_MAPPING = {
        "academic_scientific_organisation": "Academia-ScientificOrganisation",
        "company": "Company",
        "industry_consortium": "IndustryConsortium",
        "local_authority": "LocalAuthority",
        "national_authority": "NationalAuthority",
        "non_governmental_organisation": "NonGovernmentalOrganisation",
        "non_profit_organisation": "NonProfitOrganisation",
        "private_individuals": "PrivateIndividual(s)",
        "regional_authority": "RegionalAuthority",
        "standardisation_body": "StandardisationBody",
        "supra_national_authority": "SupraNationalAuthority",
    }
    # Data type to XSD mapping
    DCA_TO_XSD_MAPPING = {
        "string": XSD.string,
        "integer": XSD.integer,
        "float": XSD.float,
        "boolean": XSD.boolean,
        "date": XSD.date,
        "datetime": XSD.dateTime,
    }

    AVAILABILITY_OPTIONS = {
        "http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE": "Available",  # NOSONAR
        "http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL": "Experimental",  # NOSONAR
        "http://publications.europa.eu/resource/authority/planned-availability/STABLE": "Stable",  # NOSONAR
        "http://publications.europa.eu/resource/authority/planned-availability/TEMPORARY": "Temporary",  # NOSONAR
    }

    # Format to media type mapping
    FORMAT_TO_MEDIA_TYPE = {
        CatalogueFormat.RDF: "application/rdf+xml",
        CatalogueFormat.JSONLD: "application/ld+json",
        # Default case handled in method
    }

    # Format to RDFLib serialization format mapping
    FORMAT_TO_RDFLIB = {
        CatalogueFormat.RDF: "pretty-xml",
        CatalogueFormat.JSONLD: "json-ld",
        # Default case handled in method
    }

    @classmethod
    def map_org_type(cls, org_type: str) -> str:
        """Map organization type to ADMS publisher type."""
        return cls.ORG_TYPE_MAPPING.get(org_type, "NationalAuthority")

    @classmethod
    def map_dca_to_xsd_type(cls, dca_type: str) -> URIRef:
        """Map DCA data type to XSD type URI."""
        return cls.DCA_TO_XSD_MAPPING.get(dca_type.lower(), XSD.string)

    @classmethod
    def map_xsd_to_dca_type(cls, xsd_type_uri: str) -> str:
        """Map XSD type URI to DCA data type."""
        # Create reverse mapping
        xsd_to_dca = {str(v): k.capitalize() for k, v in cls.DCA_TO_XSD_MAPPING.items()}
        # Normalize the URI string
        xsd_type_str = str(xsd_type_uri)
        # Try direct match first
        dca_type = xsd_to_dca.get(xsd_type_str)
        if dca_type:
            return dca_type
        # Try to match by suffix (e.g., "string" from "http://www.w3.org/2001/XMLSchema#string")
        for xsd_uri, dca in xsd_to_dca.items():
            if xsd_type_str.endswith("#" + xsd_uri.split("#")[-1]):
                return dca
        # Default to String
        return "String"

    @classmethod
    def map_media_type(cls, format_type: str) -> str:
        """Map catalogue format to media type."""
        return cls.FORMAT_TO_MEDIA_TYPE.get(format_type, "text/turtle")

    @classmethod
    def map_rdflib_format(cls, format_type: str) -> str:
        """Map catalogue format to RDFLib serialization format."""
        return cls.FORMAT_TO_RDFLIB.get(format_type, "ttl")

    @classmethod
    def map_availability(cls, availability_uri: str) -> str:
        """Map availability URI to human-readable string."""
        return cls.AVAILABILITY_OPTIONS.get(availability_uri, "Unknown")
