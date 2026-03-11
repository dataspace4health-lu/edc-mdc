from pydantic import BaseModel, ConfigDict, model_validator, Field
from typing import Optional, List, Annotated
from models.data_dictionary import DataDictionaryEntry


class AddDataDictionaryEntry(BaseModel):
    field_name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Field name (alphanumeric + underscore, starts with letter)",
        ),
    ]
    description: Annotated[
        str,
        Field(
            min_length=1,
            max_length=1000,
            description="Field description (1-1000 characters)",
        ),
    ]
    data_type: Annotated[
        str,
        Field(min_length=1, max_length=20, description="Data type from allowed list"),
    ]
    personally_identifiable_variable: Optional[bool] = None
    required: Optional[bool] = None
    max_allowed_value: Optional[
        Annotated[float, Field(description="Maximum allowed value")]
    ] = None
    min_allowed_value: Optional[
        Annotated[float, Field(description="Minimum allowed value")]
    ] = None
    variable_unit: Optional[
        Annotated[
            str, Field(max_length=50, description="Variable unit (max 50 characters)")
        ]
    ] = None
    allowed_values: Optional[
        Annotated[
            str,
            Field(
                max_length=2000,
                description="Comma-separated allowed values (max 2000 characters)",
            ),
        ]
    ] = None
    allowed_values_description: Optional[
        Annotated[
            str,
            Field(
                max_length=1000,
                description="Description of allowed values (max 1000 characters)",
            ),
        ]
    ] = None
    table_name: Optional[
        Annotated[
            str,
            Field(max_length=100, description="Table name (alphanumeric + underscore)"),
        ]
    ] = None
    privacy_risk_type: Optional[
        Annotated[
            str,
            Field(max_length=50, description="Privacy risk type (max 50 characters)"),
        ]
    ] = None

    @model_validator(mode="after")
    def validate_data_type(cls, obj):
        # Map common lowercase variants to proper case
        type_mapping = {
            "string": "String",
            "integer": "Integer",
            "int": "Integer",
            "boolean": "Boolean",
            "bool": "Boolean",
            "float": "Float",
            "character": "Character",
            "char": "Character",
            "byte": "Byte",
            "short": "Short",
            "long": "Long",
            "double": "Double",
            "date": "Date",
        }

        # Normalize the data type
        normalized_type = type_mapping.get(obj.data_type.lower(), obj.data_type)

        allowed_types = {
            "String",
            "Integer",
            "Boolean",
            "Float",
            "Character",
            "Byte",
            "Short",
            "Long",
            "Double",
            "Date",
        }

        if normalized_type not in allowed_types:
            raise ValueError(f"Invalid data type. Allowed types are: {allowed_types}")

        # Update the object with the normalized type
        obj.data_type = normalized_type
        return obj

    # enable later when this is needed
    # @model_validator(mode="after")
    # def validate_privacy_risk_types(cls, obj):
    #     if obj.personally_identifiable_variable:
    #         if obj.privacy_risk_types is None:
    #             raise ValueError(
    #                 f"Privacy risk type cannot be empty, when personally_identifiable_variable is true"
    #             )
    #     return obj


class ResourceDataDictionaryEntry(BaseModel):
    id: Optional[int] = None
    field_name: str
    description: str
    data_type: str
    personally_identifiable_variable: Optional[bool] = None
    required: Optional[bool] = None
    max_allowed_value: Optional[float] = None
    min_allowed_value: Optional[float] = None
    variable_unit: Optional[str] = None
    allowed_values: Optional[str] = None
    allowed_values_description: Optional[str] = None
    table_name: Optional[str] = None
    dataset_id: Optional[int] = None
    is_authentic_source: Optional[bool] = None
    privacy_risk_type: Optional[str] = None
    position: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


def data_dictionary_entity_to_resource(
    data_dictionary: DataDictionaryEntry,
) -> ResourceDataDictionaryEntry:
    return ResourceDataDictionaryEntry(
        id=data_dictionary.id,
        field_name=data_dictionary.field_name,
        description=data_dictionary.description,
        data_type=data_dictionary.data_type,
        personally_identifiable_variable=data_dictionary.personally_identifiable_variable,
        required=data_dictionary.required,
        max_allowed_value=data_dictionary.max_allowed_value,
        min_allowed_value=data_dictionary.min_allowed_value,
        variable_unit=data_dictionary.variable_unit,
        allowed_values=data_dictionary.allowed_values,
        allowed_values_description=data_dictionary.allowed_values_description,
        table_name=data_dictionary.table_name,
        dataset_id=data_dictionary.dataset_id,
        is_authentic_source=data_dictionary.is_authentic_source,
        privacy_risk_type=data_dictionary.privacy_risk_type,
        position=data_dictionary.position,
    )


class UpdateAuthenticSourceDto(BaseModel):
    entry_id: Annotated[int, Field(gt=0, description="Must be a positive integer")]
    is_authentic_source: bool

    class Config:
        extra = "forbid"


class BulkUpdateAuthenticSourceDto(BaseModel):
    entries: Annotated[
        List[UpdateAuthenticSourceDto],
        Field(min_length=1, max_length=100, description="1-100 entries allowed"),
    ]

    class Config:
        extra = "forbid"


class UpdatePositionDto(BaseModel):
    entry_id: Annotated[int, Field(gt=0, description="Must be a positive integer")]
    position: Annotated[int, Field(ge=0, description="Position must be non-negative")]

    class Config:
        extra = "forbid"


class BulkUpdatePositionDto(BaseModel):
    updates: Annotated[
        List[UpdatePositionDto],
        Field(min_length=1, max_length=1000, description="1-1000 entries allowed"),
    ]

    class Config:
        extra = "forbid"
