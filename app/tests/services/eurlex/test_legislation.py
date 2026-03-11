import pytest
from services.eurlex.legislation import EurlexApplicableLegislationService


class TestBuildExpertQuery:
    """Tests for _build_expert_query method"""

    def test_build_query_empty_filter(self):
        """Should return default query for empty filter"""
        query = EurlexApplicableLegislationService._build_expert_query("")
        assert query == "FM=REGULATION OR FM=DIRECTIVE OR FM=DECISION"

    def test_build_query_with_eli_url_directive(self):
        """Should build DN query for ELI directive URL"""
        url = "https://eur-lex.europa.eu/eli/dir/2007/60/oj?locale=fr"
        query = EurlexApplicableLegislationService._build_expert_query(url)
        assert query == "DN=32007L0060"

    def test_build_query_with_eli_url_regulation(self):
        """Should build DN query for ELI regulation URL"""
        url = "http://data.europa.eu/eli/reg/2018/1725/oj"
        query = EurlexApplicableLegislationService._build_expert_query(url)
        assert query == "DN=32018R1725"

    def test_build_query_with_eli_url_decision(self):
        """Should build DN query for ELI decision URL"""
        url = "http://data.europa.eu/eli/dec/2019/456/oj"
        query = EurlexApplicableLegislationService._build_expert_query(url)
        assert query == "DN=32019D0456"

    def test_build_query_with_celex_url(self):
        """Should build DN query for CELEX URL"""
        url = "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:51991IP0963"
        query = EurlexApplicableLegislationService._build_expert_query(url)
        assert query == "DN=51991IP0963"

    def test_build_query_with_celex_uri(self):
        """Should build DN query for CELEX URI"""
        uri = "CELEX:32018R1725"
        query = EurlexApplicableLegislationService._build_expert_query(uri)
        assert query == "DN=32018R1725"

    def test_build_query_with_raw_celex(self):
        """Should build DN query for raw CELEX identifier"""
        celex = "31981R1653"
        query = EurlexApplicableLegislationService._build_expert_query(celex)
        assert query == "DN=31981R1653"

    def test_build_query_with_simple_text(self):
        """Should build title search query for simple text"""
        text = "transport"
        query = EurlexApplicableLegislationService._build_expert_query(text)
        assert query == "TI~transport"

    def test_build_query_with_resolution_uppercase(self):
        """Should build title search for text containing 'RESOLUTION'"""
        text = "RESOLUTION on the situation in India"
        query = EurlexApplicableLegislationService._build_expert_query(text)
        assert query == "TI~RESOLUTION on the situation in India"

    def test_build_query_with_resolution_lowercase(self):
        """Should build title search for text containing 'resolution'"""
        text = "resolution on the situation in India"
        query = EurlexApplicableLegislationService._build_expert_query(text)
        assert query == "TI~resolution on the situation in India"

    def test_build_query_with_expert_query_and_operator(self):
        """Should pass through expert query with AND operator"""
        expert = "FM=REGULATION AND TI~environment"
        query = EurlexApplicableLegislationService._build_expert_query(expert)
        assert query == expert

    def test_build_query_with_expert_query_or_operator(self):
        """Should pass through expert query with OR operator"""
        expert = "FM=REGULATION OR FM=DIRECTIVE"
        query = EurlexApplicableLegislationService._build_expert_query(expert)
        assert query == expert

    def test_build_query_with_expert_query_not_operator(self):
        """Should pass through expert query with NOT operator"""
        expert = "FM=REGULATION NOT TI~transport"
        query = EurlexApplicableLegislationService._build_expert_query(expert)
        assert query == expert

    def test_build_query_with_dn_field(self):
        """Should pass through expert query with DN field"""
        expert = "DN=32000*"
        query = EurlexApplicableLegislationService._build_expert_query(expert)
        assert query == expert

    def test_build_query_with_ti_field(self):
        """Should pass through expert query with TI field"""
        expert = "TI~transport"
        query = EurlexApplicableLegislationService._build_expert_query(expert)
        assert query == expert

    def test_build_query_with_fm_field(self):
        """Should pass through expert query with FM field"""
        expert = "FM=REGULATION"
        query = EurlexApplicableLegislationService._build_expert_query(expert)
        assert query == expert

    def test_build_query_with_tilde_operator(self):
        """Should pass through query with tilde operator"""
        expert = "TI~water"
        query = EurlexApplicableLegislationService._build_expert_query(expert)
        assert query == expert

    def test_build_query_with_equals_operator(self):
        """Should pass through query with equals operator"""
        expert = "FM=DECISION"
        query = EurlexApplicableLegislationService._build_expert_query(expert)
        assert query == expert

    def test_build_query_does_not_match_or_in_text(self):
        """Should not treat 'OR' substring in text as operator"""
        text = "information"
        query = EurlexApplicableLegislationService._build_expert_query(text)
        assert query == "TI~information"

    def test_build_query_does_not_match_and_in_text(self):
        """Should not treat 'AND' substring in text as operator"""
        text = "land"
        query = EurlexApplicableLegislationService._build_expert_query(text)
        assert query == "TI~land"
