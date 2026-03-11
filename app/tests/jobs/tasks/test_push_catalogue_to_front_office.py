import pytest
from unittest.mock import Mock, patch, MagicMock
from redis.exceptions import LockError

from jobs.tasks.push_catalogue_to_front_office import (
    push_catalogue_to_front_office_task,
)
from schemas.front_office_publishing import (
    FrontOfficePublishingResult,
    FilePublishingResult,
    PublishingStatus,
)
from schemas.catalogue import CatalogueFormat


class TestPushCatalogueToFrontOfficeTask:

    @pytest.fixture
    def mock_redis_lock(self):
        with patch(
            "jobs.tasks.push_catalogue_to_front_office.redis_client"
        ) as mock_redis:
            mock_lock = MagicMock()
            mock_lock.acquire.return_value = True
            mock_redis.lock.return_value = mock_lock
            yield mock_lock

    @pytest.fixture
    def mock_db_session(self):
        with patch(
            "jobs.tasks.push_catalogue_to_front_office.get_script_db_session"
        ) as mock_get_session:
            mock_session = Mock()
            mock_get_session.return_value = mock_session
            yield mock_session

    @pytest.fixture
    def mock_catalogue_service(self):
        with patch(
            "jobs.tasks.push_catalogue_to_front_office.CatalogueService"
        ) as mock_service:
            mock_instance = Mock()
            mock_instance.get_catalogue.return_value = (
                "application/rdf+xml",
                "<rdf>test catalogue content</rdf>",
            )
            mock_service.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_front_office_service(self):
        with patch(
            "jobs.tasks.push_catalogue_to_front_office.BaseFrontOfficeService"
        ) as mock_service:
            mock_instance = Mock()
            mock_instance.publish_files.return_value = FrontOfficePublishingResult(
                timestamp="20260113_095000",
                files=[
                    FilePublishingResult(
                        filename="catalogue.rdf",
                        remote_path="/upload/catalogue.rdf",
                        publishing_status=PublishingStatus.SUCCESS,
                        error=None,
                    )
                ],
            )
            mock_service.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_all_dependencies(
        self,
        mock_redis_lock,
        mock_db_session,
        mock_catalogue_service,
        mock_front_office_service,
    ):
        with patch(
            "jobs.tasks.push_catalogue_to_front_office.DatasetRepository"
        ), patch(
            "jobs.tasks.push_catalogue_to_front_office.ApplicableLegislationRepository"
        ), patch(
            "jobs.tasks.push_catalogue_to_front_office.DataServiceRepository"
        ), patch(
            "jobs.tasks.push_catalogue_to_front_office.DataDictionaryRepository"
        ), patch(
            "jobs.tasks.push_catalogue_to_front_office.DatasetPermissionsService"
        ), patch(
            "jobs.tasks.push_catalogue_to_front_office.ConfigService"
        ):
            yield

    def test_push_catalogue_success(
        self,
        mock_all_dependencies,
        mock_catalogue_service,
        mock_front_office_service,
        mock_db_session,
        mock_redis_lock,
    ):
        result = push_catalogue_to_front_office_task()

        assert result["status"] == "success"
        assert result["timestamp"] == "20260113_095000"
        assert result["files_count"] == 1

        mock_catalogue_service.get_catalogue.assert_called_once_with(
            CatalogueFormat.RDF, only_non_public_access=True
        )
        mock_front_office_service.publish_files.assert_called_once()

        call_args = mock_front_office_service.publish_files.call_args
        assert call_args.kwargs["base_filename"] == "catalogue"
        assert CatalogueFormat.RDF in call_args.kwargs["files_data"]

        mock_db_session.close.assert_called_once()
        mock_redis_lock.release.assert_called_once()

    def test_push_catalogue_already_running(self, mock_db_session):
        with patch(
            "jobs.tasks.push_catalogue_to_front_office.redis_client"
        ) as mock_redis:
            mock_lock = MagicMock()
            mock_lock.acquire.return_value = False
            mock_redis.lock.return_value = mock_lock

            result = push_catalogue_to_front_office_task()

            assert result["skipped"] is True
            assert result["reason"] == "already_running"
            mock_db_session.close.assert_not_called()

    def test_push_catalogue_rdf_generation_fails(
        self,
        mock_all_dependencies,
        mock_catalogue_service,
        mock_db_session,
        mock_redis_lock,
    ):
        mock_catalogue_service.get_catalogue.side_effect = Exception(
            "RDF generation failed"
        )

        with pytest.raises(Exception, match="RDF generation failed"):
            push_catalogue_to_front_office_task()

        mock_db_session.close.assert_called_once()
        mock_redis_lock.release.assert_called_once()

    def test_push_catalogue_ftp_upload_fails(
        self,
        mock_all_dependencies,
        mock_catalogue_service,
        mock_front_office_service,
        mock_db_session,
        mock_redis_lock,
    ):
        mock_front_office_service.publish_files.side_effect = Exception(
            "FTP upload failed"
        )

        with pytest.raises(Exception, match="FTP upload failed"):
            push_catalogue_to_front_office_task()

        mock_catalogue_service.get_catalogue.assert_called_once()
        mock_db_session.close.assert_called_once()
        mock_redis_lock.release.assert_called_once()

    def test_lock_release_on_lock_error(
        self,
        mock_all_dependencies,
        mock_catalogue_service,
        mock_front_office_service,
        mock_db_session,
        mock_redis_lock,
    ):
        mock_redis_lock.release.side_effect = LockError("Lock already released")

        result = push_catalogue_to_front_office_task()

        assert result["status"] == "success"
        mock_db_session.close.assert_called_once()

    def test_cleanup_happens_even_on_failure(
        self,
        mock_all_dependencies,
        mock_catalogue_service,
        mock_db_session,
        mock_redis_lock,
    ):
        mock_catalogue_service.get_catalogue.side_effect = Exception("Test failure")

        with pytest.raises(Exception):
            push_catalogue_to_front_office_task()

        mock_db_session.close.assert_called_once()
        mock_redis_lock.release.assert_called_once()
