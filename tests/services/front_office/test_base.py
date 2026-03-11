import pytest
import os
from unittest.mock import Mock, patch
from services.front_office.base import BaseFrontOfficeService
from schemas.front_office_publishing import (
    PublishingStatus,
    FrontOfficePublishingResult,
)


class TestBaseFrontOfficeService:
    @pytest.fixture
    def service(self):
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
            return BaseFrontOfficeService()

    @patch("services.front_office.base.FTP_TLS")
    def test_establish_connection_ftps_success(self, mock_ftps_class, service):
        mock_ftps = Mock()
        mock_ftps_class.return_value = mock_ftps

        connection = service._establish_connection()

        assert connection == mock_ftps
        mock_ftps.connect.assert_called_once_with("localhost", 21)
        mock_ftps.login.assert_called_once_with("testuser", "testpass")
        mock_ftps.prot_c.assert_called_once()

    @patch("services.front_office.base.FTP")
    @patch("services.front_office.base.FTP_TLS")
    def test_establish_connection_ftp_fallback(
        self, mock_ftps_class, mock_ftp_class, service
    ):
        mock_ftps = Mock()
        mock_ftps.connect.side_effect = Exception("FTPS failed")
        mock_ftps_class.return_value = mock_ftps

        mock_ftp = Mock()
        mock_ftp_class.return_value = mock_ftp

        connection = service._establish_connection()

        assert connection == mock_ftp
        mock_ftp.connect.assert_called_once_with("localhost", 21)
        mock_ftp.login.assert_called_once_with("testuser", "testpass")

    def test_close_connection_success(self, service):
        mock_connection = Mock()

        service._close_connection(mock_connection)

        mock_connection.quit.assert_called_once()

    def test_get_file_extension(self, service):
        from schemas.catalogue import CatalogueFormat

        assert service._get_file_extension(CatalogueFormat.RDF) == "rdf"
        assert service._get_file_extension(CatalogueFormat.TTL) == "ttl"
        assert service._get_file_extension(CatalogueFormat.JSONLD) == "jsonld"
        assert service._get_file_extension("CSV") == "csv"
        assert service._get_file_extension("RDF_MASTER") == "rdf"
        assert service._get_file_extension("unknown_format") == "txt"

    @patch("tempfile.NamedTemporaryFile")
    @patch("builtins.open")
    @patch("os.unlink")
    def test_upload_file_success(self, mock_unlink, mock_open, mock_temp_file, service):
        mock_temp_file.return_value.__enter__.return_value.name = "/tmp/test"
        mock_file_handle = Mock()
        mock_open.return_value.__enter__.return_value = mock_file_handle

        mock_connection = Mock()

        result = service._upload_file(mock_connection, "test content", "test.txt")

        assert result.filename == "test.txt"
        assert result.remote_path == "/test/test.txt"
        assert result.publishing_status == PublishingStatus.SUCCESS
        assert result.error is None

        mock_connection.storbinary.assert_called_once_with(
            "STOR test.txt", mock_file_handle
        )
        mock_unlink.assert_called_once_with("/tmp/test")

    @patch("tempfile.NamedTemporaryFile")
    @patch("builtins.open")
    @patch("os.unlink")
    def test_upload_file_failure(self, mock_unlink, mock_open, mock_temp_file, service):
        mock_temp_file.return_value.__enter__.return_value.name = "/tmp/test"
        mock_open.return_value.__enter__.return_value = Mock()

        mock_connection = Mock()
        mock_connection.storbinary.side_effect = Exception("Upload failed")

        result = service._upload_file(mock_connection, "test content", "test.txt")

        assert result.filename == "test.txt"
        assert result.remote_path == "/test/test.txt"
        assert result.publishing_status == PublishingStatus.FAILED
        assert "Upload failed" in result.error

        mock_unlink.assert_called_once_with("/tmp/test")

    @patch("services.front_office.base.FTP")
    @patch("services.front_office.base.FTP_TLS")
    def test_publish_files_success(self, mock_ftps_class, mock_ftp_class, service):
        # Mock FTPS failure to trigger FTP fallback
        mock_ftps = Mock()
        mock_ftps.connect.side_effect = Exception("FTPS failed")
        mock_ftps_class.return_value = mock_ftps

        mock_ftp = Mock()
        mock_ftp_class.return_value = mock_ftp

        with patch.object(service, "_upload_file") as mock_upload:
            mock_upload.return_value = Mock(
                filename="test.rdf",
                remote_path="/test/test.rdf",
                publishing_status=PublishingStatus.SUCCESS,
                error=None,
            )

            files_data = {"RDF": "<rdf>content</rdf>", "TTL": "@prefix content."}

            result = service.publish_files(files_data, "test_dataset")

            assert isinstance(result, FrontOfficePublishingResult)
            assert len(result.files) == 2
            assert mock_upload.call_count == 2
            mock_ftp.cwd.assert_called_once_with("/test")
            mock_ftp.quit.assert_called_once()

    @patch("services.front_office.base.FTP")
    @patch("services.front_office.base.FTP_TLS")
    def test_list_files_success(self, mock_ftps_class, mock_ftp_class, service):
        """Test successful file listing."""
        # Mock FTPS failure to trigger FTP fallback
        mock_ftps = Mock()
        mock_ftps.connect.side_effect = Exception("FTPS failed")
        mock_ftps_class.return_value = mock_ftps

        mock_ftp = Mock()
        mock_ftp.nlst.return_value = ["test.rdf", "test.ttl", ".hidden"]
        mock_ftp.size.return_value = 1024
        mock_ftp.sendcmd.return_value = "213 20231201120000"
        mock_ftp_class.return_value = mock_ftp

        files = service.list_files()

        # Should return 2 files (excluding .hidden)
        assert len(files) == 2
        assert files[0].filename == "test.rdf"
        assert files[1].filename == "test.ttl"
        assert all(f.size_bytes == 1024 for f in files)
        mock_ftp.cwd.assert_called_once_with("/test")
        mock_ftp.quit.assert_called_once()

    @patch("services.front_office.base.FTP")
    @patch("services.front_office.base.FTP_TLS")
    def test_publish_files_with_dataset_id_filename_pattern(
        self, mock_ftps_class, mock_ftp_class, service
    ):
        # Mock FTPS failure to trigger FTP fallback
        mock_ftps = Mock()
        mock_ftps.connect.side_effect = Exception("FTPS failed")
        mock_ftps_class.return_value = mock_ftps

        mock_ftp = Mock()
        mock_ftp_class.return_value = mock_ftp

        with patch.object(service, "_upload_file") as mock_upload:
            mock_upload.return_value = Mock(
                filename="test.rdf",
                remote_path="/test/test.rdf",
                publishing_status=PublishingStatus.SUCCESS,
                error=None,
            )

            from schemas.catalogue import CatalogueFormat

            files_data = {
                CatalogueFormat.RDF: "<rdf>content</rdf>",
                "CSV": "field_name,description\ntest,test description",
            }

            result = service.publish_files(files_data, "test_dataset", dataset_id=123)

            assert isinstance(result, FrontOfficePublishingResult)
            assert len(result.files) == 2
            assert mock_upload.call_count == 2

            # Check that files were uploaded with correct names
            upload_calls = mock_upload.call_args_list
            filenames_used = [
                call[0][2] for call in upload_calls
            ]  # Third argument is filename

            # RDF should have dataset_id appended
            assert "test_dataset-123.rdf" in filenames_used
            # CSV should have data-dictionary appended
            assert "test_dataset-data-dictionary.csv" in filenames_used

    @patch("services.front_office.base.FTP")
    @patch("services.front_office.base.FTP_TLS")
    def test_publish_files_with_rdf_master_filename(
        self, mock_ftps_class, mock_ftp_class, service
    ):
        """Test that RDF_MASTER files are named with -master suffix."""
        # Mock FTPS failure to trigger FTP fallback
        mock_ftps = Mock()
        mock_ftps.connect.side_effect = Exception("FTPS failed")
        mock_ftps_class.return_value = mock_ftps

        mock_ftp = Mock()
        mock_ftp_class.return_value = mock_ftp

        with patch.object(service, "_upload_file") as mock_upload:
            mock_upload.return_value = Mock(
                filename="test.rdf",
                remote_path="/test/test.rdf",
                publishing_status=PublishingStatus.SUCCESS,
                error=None,
            )

            from schemas.catalogue import CatalogueFormat

            files_data = {
                "RDF_MASTER": "<rdf>master_content</rdf>",
                CatalogueFormat.RDF: "<rdf>export_content</rdf>",
            }

            result = service.publish_files(files_data, "test_dataset", dataset_id=123)

            assert isinstance(result, FrontOfficePublishingResult)
            assert len(result.files) == 2
            assert mock_upload.call_count == 2

            # Check that files were uploaded with correct names
            upload_calls = mock_upload.call_args_list
            filenames_used = [
                call[0][2] for call in upload_calls
            ]  # Third argument is filename

            # RDF_MASTER should have -master suffix
            assert "test_dataset-123-master.rdf" in filenames_used
            # Regular RDF export should not have -master
            assert "test_dataset-123.rdf" in filenames_used
