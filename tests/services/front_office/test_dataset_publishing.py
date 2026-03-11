import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException

from services.front_office.dataset_publishing import FrontOfficeDatasetPublishingService
from schemas.front_office_publishing import (
    PublishingStatus,
    FrontOfficePublishingResult,
)
from models.dataset import DatasetStatus
from models.identity_context import IdentityContext


class TestFrontOfficeDatasetPublishingService:

    @pytest.fixture
    def mock_dependencies(self):
        catalogue_service = Mock()
        data_dictionary_service = Mock()
        dataset_repository = Mock()

        return {
            "catalogue_service": catalogue_service,
            "data_dictionary_service": data_dictionary_service,
            "dataset_repository": dataset_repository,
        }

    @pytest.fixture
    def service(self, mock_dependencies):
        """Create service with mocked dependencies."""
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
            return FrontOfficeDatasetPublishingService(
                catalogue_service=mock_dependencies["catalogue_service"],
                data_dictionary_service=mock_dependencies["data_dictionary_service"],
                dataset_repository=mock_dependencies["dataset_repository"],
            )

    def test_validate_dataset_not_found(self, service, mock_dependencies):
        """Test error when dataset is not found."""
        mock_dependencies["dataset_repository"].get_dataset_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service._validate_dataset(123)

        assert exc_info.value.status_code == 404
        assert "Dataset with id 123 not found" in str(exc_info.value.detail)

    def test_validate_dataset_not_published(self, service, mock_dependencies):
        mock_dataset = Mock()
        mock_dataset.status = DatasetStatus.DRAFT.value
        mock_dependencies["dataset_repository"].get_dataset_by_id.return_value = (
            mock_dataset
        )

        with pytest.raises(HTTPException) as exc_info:
            service._validate_dataset(123)

        assert exc_info.value.status_code == 400
        assert "Dataset must be PUBLISHED" in str(exc_info.value.detail)

    def test_validate_dataset_approved_with_released_at(
        self, service, mock_dependencies
    ):
        mock_dataset = Mock()
        mock_dataset.status = DatasetStatus.APPROVED.value
        mock_dataset.released_at = "2023-12-01T12:00:00Z"  # Previously published
        mock_dependencies["dataset_repository"].get_dataset_by_id.return_value = (
            mock_dataset
        )

        # Should not raise an exception
        result = service._validate_dataset(123)
        assert result == mock_dataset

    def test_validate_dataset_approved_without_released_at(
        self, service, mock_dependencies
    ):
        mock_dataset = Mock()
        mock_dataset.status = DatasetStatus.APPROVED.value
        mock_dataset.released_at = None  # Never published
        mock_dependencies["dataset_repository"].get_dataset_by_id.return_value = (
            mock_dataset
        )

        with pytest.raises(HTTPException) as exc_info:
            service._validate_dataset(123)

        assert exc_info.value.status_code == 400
        assert "Dataset must be PUBLISHED" in str(exc_info.value.detail)

    def test_validate_dataset_deprecated(self, service, mock_dependencies):
        mock_dataset = Mock()
        mock_dataset.status = DatasetStatus.DEPRECATED.value
        mock_dependencies["dataset_repository"].get_dataset_by_id.return_value = (
            mock_dataset
        )

        # Should not raise an exception
        result = service._validate_dataset(123)
        assert result == mock_dataset

    def test_generate_catalogue_data_success(self, service, mock_dependencies):
        mock_dependencies[
            "catalogue_service"
        ].get_individual_dataset_catalogue.side_effect = [
            (
                "application/rdf+xml",
                "<rdf>master_content</rdf>",
            ),  # Master RDF with versions
            ("application/rdf+xml", "<rdf>export_content</rdf>"),  # Export RDF
            ("text/turtle", "@prefix content."),  # Export TTL
            ("application/ld+json", '{"@context": "content"}'),  # Export JSON-LD
        ]

        identity = IdentityContext(user_id=1, roles=[], permissions=[])
        result = service._generate_catalogue_data(123, identity)

        from schemas.catalogue import CatalogueFormat

        assert len(result) == 4  # Master + 3 export formats
        assert "RDF_MASTER" in result.keys()
        assert CatalogueFormat.RDF in result.keys()
        assert CatalogueFormat.TTL in result.keys()
        assert CatalogueFormat.JSONLD in result.keys()
        assert result["RDF_MASTER"] == "<rdf>master_content</rdf>"

    def test_generate_and_publish_dataset_catalogues_success(
        self, service, mock_dependencies
    ):
        # Setup dataset validation
        mock_dataset = Mock()
        mock_dataset.status = DatasetStatus.PUBLISHED.value
        mock_dataset.identifier = "test-dataset"
        mock_dependencies["dataset_repository"].get_dataset_by_id.return_value = (
            mock_dataset
        )

        # Setup catalogue generation (4 calls: master + 3 exports)
        mock_dependencies[
            "catalogue_service"
        ].get_individual_dataset_catalogue.side_effect = [
            ("application/rdf+xml", "<rdf>master_content</rdf>"),
            ("application/rdf+xml", "<rdf>export_content</rdf>"),
            ("text/turtle", "@prefix content."),
            ("application/ld+json", '{"@context": "content"}'),
        ]

        # Mock publish_files method
        with patch.object(service, "publish_files") as mock_publish:
            mock_publish.return_value = FrontOfficePublishingResult(
                timestamp="20231201_120000", files=[]
            )

            identity = IdentityContext(user_id=1, roles=[], permissions=[])
            result = service.generate_and_publish_dataset_catalogues(123, identity)

            assert isinstance(result, FrontOfficePublishingResult)
            mock_publish.assert_called_once()

            # Verify publish_files was called with correct parameters
            call_args = mock_publish.call_args
            assert call_args.kwargs["base_filename"] == "test-dataset"
            assert call_args.kwargs["dataset_id"] == 123
            assert len(call_args.kwargs["files_data"]) == 4  # Master + 3 export formats
            assert "RDF_MASTER" in call_args.kwargs["files_data"]

    def test_generate_data_dictionary_csv_success(self, service, mock_dependencies):
        """Test successful data dictionary CSV generation."""
        # Mock data dictionaries exist
        mock_dependencies[
            "data_dictionary_service"
        ].get_data_dictionaries_by_dataset_id.return_value = [{"name": "test"}]

        # Mock CSV response with async iterator
        async def mock_async_iterator():
            yield b"header1,header2\n"
            yield b"value1,value2\n"

        mock_csv_response = Mock()
        mock_csv_response.body_iterator = mock_async_iterator()
        mock_dependencies["data_dictionary_service"].generate_csv.return_value = (
            mock_csv_response
        )

        identity = IdentityContext(user_id=1, roles=[], permissions=[])
        result = service._generate_data_dictionary_csv(123, identity)

        assert result == "header1,header2\nvalue1,value2\n"

    def test_generate_data_dictionary_csv_no_dictionaries(
        self, service, mock_dependencies
    ):
        """Test data dictionary CSV when no dictionaries exist."""
        mock_dependencies[
            "data_dictionary_service"
        ].get_data_dictionaries_by_dataset_id.return_value = []

        identity = IdentityContext(user_id=1, roles=[], permissions=[])
        result = service._generate_data_dictionary_csv(123, identity)

        assert result is None

    def test_generate_and_publish_with_csv_data_dictionary(
        self, service, mock_dependencies
    ):
        """Test successful dataset catalogue publishing with CSV data dictionary."""
        # Setup dataset validation
        mock_dataset = Mock()
        mock_dataset.status = DatasetStatus.PUBLISHED.value
        mock_dataset.identifier = "test-dataset"
        mock_dependencies["dataset_repository"].get_dataset_by_id.return_value = (
            mock_dataset
        )

        # Setup catalogue generation (4 calls: master + 3 exports)
        mock_dependencies[
            "catalogue_service"
        ].get_individual_dataset_catalogue.side_effect = [
            ("application/rdf+xml", "<rdf>master_content</rdf>"),
            ("application/rdf+xml", "<rdf>export_content</rdf>"),
            ("text/turtle", "@prefix content."),
            ("application/ld+json", '{"@context": "content"}'),
        ]

        # Mock data dictionaries exist and CSV generation
        mock_dependencies[
            "data_dictionary_service"
        ].get_data_dictionaries_by_dataset_id.return_value = [{"name": "test"}]

        async def mock_async_iterator():
            yield b"field_name,description\n"
            yield b"test_field,test description\n"

        mock_csv_response = Mock()
        mock_csv_response.body_iterator = mock_async_iterator()
        mock_dependencies["data_dictionary_service"].generate_csv.return_value = (
            mock_csv_response
        )

        # Mock publish_files method
        with patch.object(service, "publish_files") as mock_publish:
            mock_publish.return_value = FrontOfficePublishingResult(
                timestamp="20231201_120000", files=[]
            )

            identity = IdentityContext(user_id=1, roles=[], permissions=[])
            result = service.generate_and_publish_dataset_catalogues(123, identity)

            assert isinstance(result, FrontOfficePublishingResult)
            mock_publish.assert_called_once()

            # Verify publish_files was called with correct parameters including CSV
            call_args = mock_publish.call_args
            assert call_args.kwargs["base_filename"] == "test-dataset"
            assert call_args.kwargs["dataset_id"] == 123
            assert (
                len(call_args.kwargs["files_data"]) == 5
            )  # Master + 3 export formats + CSV
            assert "RDF_MASTER" in call_args.kwargs["files_data"]
            assert "CSV" in call_args.kwargs["files_data"]
            assert (
                call_args.kwargs["files_data"]["CSV"]
                == "field_name,description\ntest_field,test description\n"
            )
