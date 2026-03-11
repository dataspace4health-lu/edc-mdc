import pytest
from unittest.mock import Mock, patch

from services.front_office.keyword_publishing import (
    FrontOfficeKeywordPublishingService,
)
from schemas.front_office_publishing import FrontOfficePublishingResult


class TestFrontOfficeKeywordPublishingService:

    @pytest.fixture
    def mock_dependencies(self):
        keyword_catalogue_service = Mock()
        keyword_repository = Mock()

        return {
            "keyword_catalogue_service": keyword_catalogue_service,
            "keyword_repository": keyword_repository,
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
            return FrontOfficeKeywordPublishingService(
                keyword_catalogue_service=mock_dependencies[
                    "keyword_catalogue_service"
                ],
                keyword_repository=mock_dependencies["keyword_repository"],
            )

    def test_generate_and_publish_keywords_success(self, service, mock_dependencies):
        mock_dependencies["keyword_catalogue_service"].get_catalogue.return_value = (
            "application/rdf+xml",
            "<rdf>keywords content</rdf>",
        )

        with patch.object(service, "publish_files") as mock_publish:
            mock_publish.return_value = FrontOfficePublishingResult(
                timestamp="20231201_120000", files=[]
            )

            result = service.generate_and_publish_keywords()

            assert isinstance(result, FrontOfficePublishingResult)
            mock_publish.assert_called_once()

            call_args = mock_publish.call_args
            assert call_args.kwargs["base_filename"] == "keywords"
            assert len(call_args.kwargs["files_data"]) == 1
