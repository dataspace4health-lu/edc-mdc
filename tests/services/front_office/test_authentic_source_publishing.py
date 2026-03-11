import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from services.front_office.authentic_source_publishing import (
    FrontOfficeAuthenticSourcePublishingService,
)
from schemas.front_office_publishing import FrontOfficePublishingResult


class TestFrontOfficeAuthenticSourcePublishingService:

    @pytest.fixture
    def mock_dependencies(self):
        authentic_source_catalogue_service = Mock()
        authentic_source_repository = Mock()

        return {
            "authentic_source_catalogue_service": authentic_source_catalogue_service,
            "authentic_source_repository": authentic_source_repository,
        }

    @pytest.fixture
    def service(self, mock_dependencies):
        with patch.dict(
            "os.environ",
            {
                "FRONT_OFFICE_HOST": "localhost",
                "FRONT_OFFICE_PORT": "21",
                "FRONT_OFFICE_USER": "testuser",
                "FRONT_OFFICE_PASSWORD": "testpass",
                "FRONT_OFFICE_UPLOAD_PATH": "/test",
            },
        ):
            return FrontOfficeAuthenticSourcePublishingService(
                authentic_source_catalogue_service=mock_dependencies[
                    "authentic_source_catalogue_service"
                ],
                authentic_source_repository=mock_dependencies[
                    "authentic_source_repository"
                ],
            )

    def test_generate_catalogue_data_success(self, service, mock_dependencies):
        mock_dependencies[
            "authentic_source_catalogue_service"
        ].get_catalogue.side_effect = [
            ("application/rdf+xml", "<rdf>authentic source content</rdf>"),
            ("text/turtle", "@prefix authentic source content."),
            ("application/ld+json", '{"@context": "authentic source content"}'),
        ]

        result = service._generate_catalogue_data()

        assert len(result) == 3
        assert "RDF" in [str(k) for k in result.keys()]
        assert "TTL" in [str(k) for k in result.keys()]
        assert "JSONLD" in [str(k) for k in result.keys()]

    def test_generate_and_publish_authentic_source_success(
        self, service, mock_dependencies
    ):
        # Setup catalogue generation
        mock_dependencies[
            "authentic_source_catalogue_service"
        ].get_catalogue.side_effect = [
            ("application/rdf+xml", "<rdf>authentic source content</rdf>"),
            ("text/turtle", "@prefix authentic source content."),
            ("application/ld+json", '{"@context": "authentic source content"}'),
        ]

        # Mock publish_files method
        with patch.object(service, "publish_files") as mock_publish:
            mock_publish.return_value = FrontOfficePublishingResult(
                timestamp="20231201_120000", files=[]
            )

            result = service.generate_and_publish_authentic_source()

            assert isinstance(result, FrontOfficePublishingResult)
            mock_publish.assert_called_once()

            # Verify publish_files was called with correct parameters
            call_args = mock_publish.call_args
            assert call_args.kwargs["base_filename"] == "authentic_source"
            assert len(call_args.kwargs["files_data"]) == 3
