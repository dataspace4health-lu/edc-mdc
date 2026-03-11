import pytest
from services.eurlex.identifiers import (
    convert_eli_to_celex,
    extract_eli_from_input,
    extract_celex_from_input,
)


class TestConvertEliToCelex:
    """Tests for convert_eli_to_celex function"""

    def test_convert_directive_eli_to_celex(self):
        """Should convert directive ELI to CELEX"""
        result = convert_eli_to_celex("dir", "2007", "60")
        assert result == "32007L0060"

    def test_convert_regulation_eli_to_celex(self):
        """Should convert regulation ELI to CELEX"""
        result = convert_eli_to_celex("reg", "2018", "1725")
        assert result == "32018R1725"

    def test_convert_decision_eli_to_celex(self):
        """Should convert decision ELI to CELEX"""
        result = convert_eli_to_celex("dec", "2019", "456")
        assert result == "32019D0456"

    def test_convert_recommendation_eli_to_celex(self):
        """Should convert recommendation ELI to CELEX"""
        result = convert_eli_to_celex("rec", "2020", "123")
        assert result == "32020H0123"

    def test_convert_eli_pads_number_to_4_digits(self):
        """Should pad number to 4 digits"""
        result = convert_eli_to_celex("dir", "2007", "5")
        assert result == "32007L0005"

    def test_convert_eli_handles_uppercase_type(self):
        """Should handle uppercase ELI type"""
        result = convert_eli_to_celex("DIR", "2007", "60")
        assert result == "32007L0060"

    def test_convert_eli_returns_none_for_unknown_type(self):
        """Should return None for unknown ELI type"""
        result = convert_eli_to_celex("unknown", "2007", "60")
        assert result is None

    def test_convert_eli_returns_none_for_invalid_number(self):
        """Should return None for invalid number"""
        result = convert_eli_to_celex("dir", "2007", "abc")
        assert result is None


class TestExtractEliFromInput:
    """Tests for extract_eli_from_input function"""

    def test_extract_eli_from_eur_lex_url(self):
        """Should extract and convert ELI from EUR-Lex URL"""
        url = "https://eur-lex.europa.eu/eli/dir/2007/60/oj?locale=fr"
        result = extract_eli_from_input(url)
        assert result == "32007L0060"

    def test_extract_eli_from_data_europa_url(self):
        """Should extract and convert ELI from data.europa.eu URL"""
        url = "http://data.europa.eu/eli/dir/2007/60/oj"
        result = extract_eli_from_input(url)
        assert result == "32007L0060"

    def test_extract_eli_from_regulation_url(self):
        """Should extract and convert ELI for regulation"""
        url = "https://eur-lex.europa.eu/eli/reg/2018/1725/oj"
        result = extract_eli_from_input(url)
        assert result == "32018R1725"

    def test_extract_eli_from_decision_url(self):
        """Should extract and convert ELI for decision"""
        url = "http://data.europa.eu/eli/dec/2019/456/oj"
        result = extract_eli_from_input(url)
        assert result == "32019D0456"

    def test_extract_eli_from_path_without_domain(self):
        """Should extract and convert ELI from path without domain"""
        path = "eli/dir/2007/60/oj"
        result = extract_eli_from_input(path)
        assert result == "32007L0060"

    def test_extract_eli_without_version(self):
        """Should extract and convert ELI without version suffix"""
        url = "https://eur-lex.europa.eu/eli/dir/2007/60"
        result = extract_eli_from_input(url)
        assert result == "32007L0060"

    def test_extract_eli_returns_none_for_plain_text(self):
        """Should return None for plain text"""
        text = "transport"
        result = extract_eli_from_input(text)
        assert result is None

    def test_extract_eli_returns_none_for_celex_url(self):
        """Should return None for CELEX URL"""
        url = "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:51991IP0963"
        result = extract_eli_from_input(url)
        assert result is None


class TestExtractCelexFromInput:
    """Tests for extract_celex_from_input function"""

    def test_extract_celex_from_full_url(self):
        """Should extract CELEX from full EUR-Lex URL"""
        url = "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:51991IP0963"
        result = extract_celex_from_input(url)
        assert result == "51991IP0963"

    def test_extract_celex_from_full_url_lowercase(self):
        """Should extract CELEX from lowercase URL"""
        url = "https://eur-lex.europa.eu/legal-content/en/all/?uri=celex:51991ip0963"
        result = extract_celex_from_input(url)
        assert result == "51991ip0963"

    def test_extract_celex_from_url_with_query_params(self):
        """Should extract CELEX from URL with multiple query parameters"""
        url = "https://eur-lex.europa.eu/legal-content/EN/ALL/?foo=bar&uri=CELEX:32018R1725&baz=qux"
        result = extract_celex_from_input(url)
        assert result == "32018R1725"

    def test_extract_celex_from_uri_format(self):
        """Should extract CELEX from URI format (CELEX:...)"""
        uri = "CELEX:51991IP0963"
        result = extract_celex_from_input(uri)
        assert result == "51991IP0963"

    def test_extract_celex_from_uri_format_lowercase(self):
        """Should extract CELEX from lowercase URI"""
        uri = "celex:32018r1725"
        result = extract_celex_from_input(uri)
        assert result == "32018r1725"

    def test_extract_celex_from_raw_identifier(self):
        """Should recognize raw CELEX identifier"""
        celex = "51991IP0963"
        result = extract_celex_from_input(celex)
        assert result == "51991IP0963"

    def test_extract_celex_from_raw_identifier_lowercase(self):
        """Should recognize and uppercase raw CELEX identifier"""
        celex = "32018r1725"
        result = extract_celex_from_input(celex)
        assert result == "32018R1725"

    def test_extract_celex_from_raw_identifier_various_formats(self):
        """Should recognize various CELEX formats"""
        test_cases = [
            ("32018R1725", "32018R1725"),
            ("51991IP0963", "51991IP0963"),
            ("31981R1653", "31981R1653"),
            ("62019CJ0025", "62019CJ0025"),
        ]
        for input_val, expected in test_cases:
            result = extract_celex_from_input(input_val)
            assert result == expected

    def test_extract_celex_returns_none_for_plain_text(self):
        """Should return None for plain text search"""
        text = "transport"
        result = extract_celex_from_input(text)
        assert result is None

    def test_extract_celex_returns_none_for_text_with_resolution(self):
        """Should return None for text containing 'RESOLUTION'"""
        text = "RESOLUTION on the situation in India"
        result = extract_celex_from_input(text)
        assert result is None

    def test_extract_celex_returns_none_for_expert_query(self):
        """Should return None for expert query syntax"""
        query = "FM=REGULATION AND TI~environment"
        result = extract_celex_from_input(query)
        assert result is None
