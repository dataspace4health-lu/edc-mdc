import pytest
from unittest.mock import Mock, AsyncMock
from io import BytesIO
from fastapi import UploadFile
from services.antivirus import AntivirusService


class FakeHttpxClient:
    def __init__(self, status_code, json_payload=None):
        self.status_code = status_code
        self.json_payload = json_payload
        self.post_called = False
        self.last_url = None
        self.last_headers = None
        self.last_files = None
        self.last_data = None

    async def post(self, url, headers=None, files=None, data=None):
        self.post_called = True
        self.last_url = url
        self.last_headers = headers
        self.last_files = files
        self.last_data = data

        response = Mock()
        response.status_code = self.status_code
        if self.json_payload:
            response.json = Mock(return_value=self.json_payload)
        return response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def create_upload_file(filename="test.csv", content=b"test content"):
    file = BytesIO(content)
    upload_file = UploadFile(filename=filename, file=file)
    return upload_file


@pytest.mark.asyncio
async def test_scan_file_clean(monkeypatch):
    monkeypatch.setenv("AVSCAN_API_KEY", "test-api-key")
    monkeypatch.setenv("AVSCAN_API_URL", "https://avscan-test.example.com")

    json_payload = {
        "id": "test-scan-id",
        "code": 200,
        "status": "clean",
        "result": "The file is clean",
        "results": [
            {"scanner": "clamav", "result": "The file is clean", "status": "clean"}
        ],
    }

    fake_client = FakeHttpxClient(200, json_payload)

    service = AntivirusService()
    upload_file = create_upload_file()

    # Mock httpx.AsyncClient
    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: fake_client)

    is_clean, message = await service.scan_file(upload_file)

    assert is_clean is True
    assert message == "The file is clean"
    assert fake_client.post_called
    assert fake_client.last_url == "https://avscan-test.example.com/av/v1/scans"
    assert fake_client.last_headers["X-AVSCAN-API-KEY"] == "test-api-key"
    assert fake_client.last_data["synchronous"] == "true"


@pytest.mark.asyncio
async def test_scan_file_virus_detected(monkeypatch):
    monkeypatch.setenv("AVSCAN_API_KEY", "test-api-key")
    monkeypatch.setenv("AVSCAN_API_URL", "https://avscan-test.example.com")

    json_payload = {
        "id": "test-scan-id",
        "code": 403,
        "status": "virus",
        "result": "Virus found: mail/dvh3v",
        "results": [
            {
                "scanner": "clamav",
                "result": "Virus found: mail/dvh3v",
                "status": "virus",
            }
        ],
    }

    fake_client = FakeHttpxClient(200, json_payload)

    service = AntivirusService()
    upload_file = create_upload_file()

    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: fake_client)

    is_clean, message = await service.scan_file(upload_file)

    assert is_clean is False
    assert message == "Virus found: mail/dvh3v"


@pytest.mark.asyncio
async def test_scan_file_no_api_key_configured(monkeypatch):
    monkeypatch.delenv("AVSCAN_API_KEY", raising=False)
    monkeypatch.delenv("AVSCAN_API_URL", raising=False)

    service = AntivirusService()
    upload_file = create_upload_file()

    is_clean, message = await service.scan_file(upload_file)

    assert is_clean is True
    assert message == "Antivirus scanning disabled (no API key configured)"
