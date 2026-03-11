from typing import Dict

reciprocal_mapping: Dict[str, str] = {
    "dct:hasVersion": "dct:isVersionOf",
    "dct:isVersionOf": "dct:hasVersion",
    "dct:source": "dct:relation",
    "dct:relation": "dct:relation",
    "dct:hasPart": "dct:isPartOf",
    "dct:isPartOf": "dct:hasPart",
    "dct:conformsTo": "dct:relation",
    "dct:hasFormat": "dct:isFormatOf",
    "dct:isFormatOf": "dct:hasFormat",
    "dct:isReferencedBy": "dct:references",
    "dct:references": "dct:isReferencedBy",
    "dct:isReplacedBy": "dct:replaces",
    "dct:replaces": "dct:isReplacedBy",
    "dct:isRequiredBy": "dct:requires",
    "dct:requires": "dct:isRequiredBy",
}


def validate_relation_type(relation_type: str) -> str:
    if relation_type not in reciprocal_mapping:
        raise ValueError(f"Invalid relation type: {relation_type}")
    return relation_type
