import pytest
from utils.key_generator import KeyGenerator


def test_generate_key_from_label_basic():
    label = "Test Label"
    expected = "test_label"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_with_special_characters():
    label = "Test & Label! With @Special# Characters$"
    expected = "test_label_with_special_characters"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_with_numbers():
    label = "Test Label 123"
    expected = "test_label_123"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_with_consecutive_spaces():
    label = "Test   Multiple    Spaces"
    expected = "test_multiple_spaces"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_with_hyphens():
    label = "Test-Label-With-Hyphens"
    expected = "test_label_with_hyphens"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_with_dots():
    label = "Test.Label.With.Dots"
    expected = "test_label_with_dots"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_truncation_default():
    long_label = "a" * 150  # 150 character label
    result = KeyGenerator.generate_key_from_label(long_label)
    assert len(result) == 100
    assert result == "a" * 100


def test_generate_key_from_label_truncation_custom():
    label = "This is a very long label that should be truncated"
    max_length = 20
    result = KeyGenerator.generate_key_from_label(label, max_length)
    assert len(result) <= max_length
    assert result == "this_is_a_very_long"


def test_generate_key_from_label_trailing_underscores():
    label = "Test Label!!!"
    expected = "test_label"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_leading_special_chars():
    label = "!!!Test Label"
    expected = "_test_label"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_empty_string():
    label = ""
    expected = ""
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_only_special_chars():
    label = "!@#$%^&*()"
    expected = ""
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_unicode_characters():
    label = "Tést Làbél with ñ and ü"
    expected = "t_st_l_b_l_with_and"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_mixed_case():
    label = "MiXeD cAsE lAbEl"
    expected = "mixed_case_label"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_with_parentheses():
    label = "Test (Label) With [Brackets]"
    expected = "test_label_with_brackets"
    result = KeyGenerator.generate_key_from_label(label)
    assert result == expected


def test_generate_key_from_label_real_world_examples():
    test_cases = [
        ("Environmental Data Collection", "environmental_data_collection"),
        ("COVID-19 Response Measures", "covid_19_response_measures"),
        ("Applicable Legislation & Compliance", "applicable_legislation_compliance"),
        ("User Registration (v2.0)", "user_registration_v2_0"),
        ("Data Quality Assessment 2024", "data_quality_assessment_2024"),
    ]

    for label, expected in test_cases:
        result = KeyGenerator.generate_key_from_label(label)
        assert result == expected, f"Failed for label: {label}"


def test_generate_key_from_label_truncation_with_underscores():
    label = "a" * 95 + "_test_"  # Will be truncated at 100 chars ending with underscore
    result = KeyGenerator.generate_key_from_label(label)
    assert len(result) <= 100
    assert not result.endswith("_")


def test_generate_key_from_label_none_input():
    result = KeyGenerator.generate_key_from_label(None)
    assert result == ""


# Tests for generate_key_from_label_and_link


def test_generate_key_from_label_and_link_with_both():
    label = "Règlement grand-ducal du 24 juillet 2024"
    link = "https://legilux.public.lu/eli/etat/leg/rect/2024/07/24/a378/jo"
    result = KeyGenerator.generate_key_from_label_and_link(label, link)

    # Should have label portion + underscore + hash
    assert result.startswith("r_glement_grand_ducal_du_24_juillet_2024_")
    assert len(result) > len("r_glement_grand_ducal_du_24_juillet_2024_")
    # Hash portion should be 12 characters
    hash_part = result.split("_")[-1]
    assert len(hash_part) == 12


def test_generate_key_from_label_and_link_different_links_different_keys():
    label = "Règlement grand-ducal du 24 juillet 2024"
    link1 = "https://legilux.public.lu/eli/etat/leg/rect/2024/07/24/a378/jo"
    link2 = "https://legilux.public.lu/eli/etat/leg/rect/2024/07/24/a379/jo"

    result1 = KeyGenerator.generate_key_from_label_and_link(label, link1)
    result2 = KeyGenerator.generate_key_from_label_and_link(label, link2)

    # Same label but different links should produce different keys
    assert result1 != result2
    # Both should have same label prefix
    assert result1.split("_")[:-1] == result2.split("_")[:-1]


def test_generate_key_from_label_and_link_same_link_same_key():
    label = "Test Legislation"
    link = "https://example.com/law/123"

    result1 = KeyGenerator.generate_key_from_label_and_link(label, link)
    result2 = KeyGenerator.generate_key_from_label_and_link(label, link)

    # Same label and link should produce identical keys
    assert result1 == result2


def test_generate_key_from_label_and_link_empty_link():
    label = "Test Legislation"
    link = ""

    result = KeyGenerator.generate_key_from_label_and_link(label, link)

    # Should fall back to label-only key (no hash appended)
    assert result == "test_legislation"
    assert "_" not in result.split("test_legislation")[-1]


def test_generate_key_from_label_and_link_none_link():
    label = "Test Legislation"
    link = None

    result = KeyGenerator.generate_key_from_label_and_link(label, link)

    # Should fall back to label-only key
    assert result == "test_legislation"


def test_generate_key_from_label_and_link_whitespace_link():
    label = "Test Legislation"
    link = "   "

    result = KeyGenerator.generate_key_from_label_and_link(label, link)

    # Should fall back to label-only key
    assert result == "test_legislation"


def test_generate_key_from_label_and_link_long_label():
    label = "A" * 100  # Very long label
    link = "https://example.com/law/123"

    result = KeyGenerator.generate_key_from_label_and_link(label, link)

    # Label should be truncated to 80 chars, then hash added
    label_portion = result.rsplit("_", 1)[0]
    hash_portion = result.rsplit("_", 1)[1]

    assert len(label_portion) == 80
    assert len(hash_portion) == 12
    assert len(result) == 80 + 1 + 12  # label + underscore + hash


def test_generate_key_from_label_and_link_empty_label():
    label = ""
    link = "https://example.com/law/123"

    result = KeyGenerator.generate_key_from_label_and_link(label, link)

    assert result == ""


def test_generate_key_from_label_and_link_real_world_examples():
    test_cases = [
        (
            "Règlement grand-ducal du 24 juillet 2024 portant rectification",
            "https://legilux.public.lu/eli/etat/leg/rect/2024/07/24/a378/jo",
        ),
        (
            "GDPR - General Data Protection Regulation",
            "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        ),
        (
            "Data Protection Act 2018",
            "http://www.legislation.gov.uk/ukpga/2018/12",
        ),
    ]

    for label, link in test_cases:
        result = KeyGenerator.generate_key_from_label_and_link(label, link)

        # Should contain both label portion and hash
        assert "_" in result
        parts = result.rsplit("_", 1)
        assert len(parts) == 2
        label_part, hash_part = parts
        assert len(label_part) > 0
        assert len(hash_part) == 12


def test_generate_key_from_label_and_link_hash_consistency():
    label = "Test Law"
    link = "https://example.com/law/123"

    # Generate key multiple times
    results = [
        KeyGenerator.generate_key_from_label_and_link(label, link) for _ in range(5)
    ]

    # All results should be identical (deterministic hashing)
    assert len(set(results)) == 1
