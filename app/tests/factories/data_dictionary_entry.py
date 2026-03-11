from models.data_dictionary import DataDictionaryEntry


def create_sample_data_dictionary_entry(  # NOSONAR
    dataset_id,
    is_authentic_source=False,
    field_name=None,
    description=None,
    data_type=None,
    personally_identifiable_variable=None,
    required=None,
    max_allowed_value=None,
    min_allowed_value=None,
    variable_unit=None,
    allowed_values=None,
    allowed_values_description=None,
    table_name=None,
    privacy_risk_type=None,
    position=None,
):
    return DataDictionaryEntry(
        field_name=field_name or "test_field",
        description=description or "Test description",
        data_type=data_type or "string",
        personally_identifiable_variable=(
            personally_identifiable_variable
            if personally_identifiable_variable is not None
            else True
        ),
        required=required if required is not None else False,
        max_allowed_value=max_allowed_value if max_allowed_value is not None else 100,
        min_allowed_value=min_allowed_value if min_allowed_value is not None else 1,
        variable_unit=variable_unit or "kg",
        allowed_values=allowed_values or "[1, 2, 3]",
        allowed_values_description=allowed_values_description
        or "[1=One, 2=Two, 3=Three]",
        is_authentic_source=is_authentic_source,
        table_name=table_name or "test_table",
        dataset_id=dataset_id,
        privacy_risk_type=privacy_risk_type or "low",
        position=position,
    )
