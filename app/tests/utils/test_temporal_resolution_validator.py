import pytest
from validators.temporal_resolution_validator import validate_temporal_resolution


class TestTemporalResolutionValidator:
    def test_none_value_returns_none(self):
        assert validate_temporal_resolution(None) is None

    def test_empty_string_returns_empty_string(self):
        assert validate_temporal_resolution("") == ""

    # Valid ISO 8601 durations - should pass
    def test_valid_duration_one_day(self):
        assert validate_temporal_resolution("P1D") == "P1D"

    def test_valid_duration_one_hour(self):
        assert validate_temporal_resolution("PT1H") == "PT1H"

    def test_valid_duration_one_month(self):
        assert validate_temporal_resolution("P1M") == "P1M"

    def test_valid_duration_one_year(self):
        assert validate_temporal_resolution("P1Y") == "P1Y"

    def test_valid_duration_one_week(self):
        assert validate_temporal_resolution("P1W") == "P1W"

    def test_valid_duration_thirty_minutes(self):
        assert validate_temporal_resolution("PT30M") == "PT30M"

    def test_valid_duration_complex(self):
        assert validate_temporal_resolution("P1Y2M3DT4H5M6S") == "P1Y2M3DT4H5M6S"

    def test_valid_duration_with_seconds_decimal(self):
        assert validate_temporal_resolution("PT1.5S") == "PT1.5S"

    def test_valid_duration_days_and_hours(self):
        assert validate_temporal_resolution("P2DT12H") == "P2DT12H"

    def test_valid_duration_multiple_digits(self):
        assert validate_temporal_resolution("P365D") == "P365D"

    # Invalid durations - should raise ValueError
    def test_invalid_negative_duration_with_minus_prefix(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("-P1D")
        assert "ISO 8601 duration format" in str(exc_info.value)
        assert "Negative values are not allowed" in str(exc_info.value)

    def test_invalid_negative_hour(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("-PT1H")
        assert "ISO 8601 duration format" in str(exc_info.value)

    def test_invalid_negative_component_in_middle(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("P-1D")
        assert "ISO 8601 duration format" in str(exc_info.value)

    def test_invalid_negative_minutes(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("PT-5M")
        assert "ISO 8601 duration format" in str(exc_info.value)

    def test_invalid_plain_number(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("10")
        assert "ISO 8601 duration format" in str(exc_info.value)

    def test_invalid_decimal_number(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("1.2")
        assert "ISO 8601 duration format" in str(exc_info.value)

    def test_invalid_random_text(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("not-a-duration")
        assert "ISO 8601 duration format" in str(exc_info.value)

    def test_invalid_missing_p_prefix(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("1D")
        assert "ISO 8601 duration format" in str(exc_info.value)

    def test_invalid_empty_duration_p_only(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("P")
        assert "must specify at least one time component" in str(exc_info.value)

    def test_invalid_empty_duration_pt_only(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("PT")
        assert "must specify at least one time component" in str(exc_info.value)

    def test_invalid_lowercase_p(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("p1d")
        assert "ISO 8601 duration format" in str(exc_info.value)

    def test_invalid_hours_without_t(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("P1H")
        assert "ISO 8601 duration format" in str(exc_info.value)

    def test_invalid_wrong_order(self):
        with pytest.raises(ValueError) as exc_info:
            validate_temporal_resolution("PT1HP1D")
        assert "ISO 8601 duration format" in str(exc_info.value)
