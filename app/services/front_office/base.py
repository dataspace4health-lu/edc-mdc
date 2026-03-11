import os
import ssl
import tempfile
from abc import ABC
from datetime import datetime
from ftplib import FTP, FTP_TLS
from typing import List, Dict, Any

from schemas.front_office_publishing import (
    FrontOfficePublishingResult,
    FilePublishingResult,
    FrontOfficeFileInfo,
    PublishingStatus,
)
from schemas.catalogue import CatalogueFormat


class BaseFrontOfficeService(ABC):
    def __init__(self):
        self.front_office_host = os.getenv("FRONT_OFFICE_HOST", "")
        self.front_office_port = int(os.getenv("FRONT_OFFICE_PORT", "21"))
        self.front_office_user = os.getenv("FRONT_OFFICE_USER", "")
        self.front_office_password = os.getenv("FRONT_OFFICE_PASSWORD", "")
        self.front_office_path = os.getenv("FRONT_OFFICE_UPLOAD_PATH", "")

    def _establish_connection(self) -> Any:
        try:
            ftps = FTP_TLS()
            ftps.context = ssl.create_default_context()
            ftps.context.check_hostname = False
            ftps.context.verify_mode = ssl.CERT_NONE
            ftps.connect(self.front_office_host, self.front_office_port)
            ftps.login(self.front_office_user, self.front_office_password)
            ftps.prot_c()
            return ftps
        except Exception:
            ftp = FTP()  # NOSONAR
            ftp.connect(self.front_office_host, self.front_office_port)
            ftp.login(self.front_office_user, self.front_office_password)
            return ftp

    def _close_connection(self, connection: Any) -> None:
        try:
            connection.quit()
        except:
            try:
                connection.close()
            except:
                pass

    def _upload_file(
        self, connection: Any, content: str, filename: str
    ) -> FilePublishingResult:
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            try:
                with open(temp_file_path, "rb") as file_handle:
                    connection.storbinary(f"STOR {filename}", file_handle)

                remote_path = (
                    f"{self.front_office_path.rstrip('/')}/{filename}"
                    if self.front_office_path
                    else filename
                )

                return FilePublishingResult(
                    filename=filename,
                    remote_path=remote_path,
                    publishing_status=PublishingStatus.SUCCESS,
                    error=None,
                )
            finally:
                os.unlink(temp_file_path)

        except Exception as e:
            return FilePublishingResult(
                filename=filename,
                remote_path=(
                    f"{self.front_office_path.rstrip('/')}/{filename}"
                    if self.front_office_path
                    else filename
                ),
                publishing_status=PublishingStatus.FAILED,
                error=str(e),
            )

    def _get_file_extension(self, format_type) -> str:
        format_mapping = {
            CatalogueFormat.RDF: "rdf",
            CatalogueFormat.TTL: "ttl",
            CatalogueFormat.JSONLD: "jsonld",
            "CSV": "csv",
            "RDF_MASTER": "rdf",
        }
        return format_mapping.get(format_type, "txt")

    def publish_files(
        self,
        files_data: Dict[str, str],
        base_filename: str,
        dataset_id: int = None,
        csv_suffix: str = "data-dictionary",
    ) -> FrontOfficePublishingResult:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_results = []

        connection = self._establish_connection()

        try:
            if self.front_office_path:
                connection.cwd(self.front_office_path)

            for format_name, content in files_data.items():
                file_extension = self._get_file_extension(format_name)

                # Generate filename based on format type
                if format_name == "CSV":
                    filename = f"{base_filename}-{csv_suffix}.{file_extension}"
                elif format_name == "RDF_MASTER":
                    # Master file with all versions for front office HTML generation
                    if dataset_id:
                        filename = (
                            f"{base_filename}-{dataset_id}-master.{file_extension}"
                        )
                    else:
                        filename = f"{base_filename}-master.{file_extension}"
                else:
                    if dataset_id:
                        filename = f"{base_filename}-{dataset_id}.{file_extension}"
                    else:
                        filename = f"{base_filename}.{file_extension}"

                result = self._upload_file(connection, content, filename)
                file_results.append(result)

        finally:
            self._close_connection(connection)

        return FrontOfficePublishingResult(timestamp=timestamp, files=file_results)

    def list_files(self) -> List[FrontOfficeFileInfo]:
        connection = self._establish_connection()

        try:
            if self.front_office_path:
                connection.cwd(self.front_office_path)

            filenames = connection.nlst()
            files = []

            for filename in filenames:
                if not filename.startswith("."):
                    remote_path = (
                        f"{self.front_office_path.rstrip('/')}/{filename}"
                        if self.front_office_path
                        else filename
                    )

                    try:
                        size_bytes = connection.size(filename)
                        modify_time_response = connection.sendcmd(f"MDTM {filename}")
                        timestamp_str = modify_time_response.split()[-1]

                        # Convert FTP MDTM format (YYYYMMDDHHMMSS) to ISO format
                        iso_timestamp = None
                        if timestamp_str and len(timestamp_str) == 14:
                            try:
                                dt = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
                                iso_timestamp = dt.isoformat() + "Z"
                            except ValueError:
                                iso_timestamp = None

                        files.append(
                            FrontOfficeFileInfo(
                                filename=filename,
                                remote_path=remote_path,
                                size_bytes=size_bytes,
                                modified_time=iso_timestamp,
                            )
                        )
                    except Exception:
                        # If size/timestamp fails, just include the filename with defaults
                        files.append(
                            FrontOfficeFileInfo(
                                filename=filename,
                                remote_path=remote_path,
                                size_bytes=0,
                                modified_time="",
                            )
                        )

            return files

        finally:
            self._close_connection(connection)
