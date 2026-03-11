import pytest
from unittest.mock import patch
from io import BytesIO
from test_factory import client_with_logged_in_user
from fastapi.testclient import TestClient
from main import app


def test_scan_file_clean(client_with_logged_in_user, monkeypatch):
    monkeypatch.setenv("AVSCAN_API_KEY", "test-key")
    monkeypatch.setenv("AVSCAN_API_URL", "https://test.example.com")

    # Mock the antivirus service
    async def mock_scan_file(self, file):
        return True, "The file is clean"

    with patch("services.antivirus.AntivirusService.scan_file", new=mock_scan_file):
        # Create a test file
        file_content = b"test file content"
        files = {
            "file": ("test.xlsx", BytesIO(file_content), "application/vnd.ms-excel")
        }

        response = client_with_logged_in_user.post(
            "/api/v1/antivirus/scan", files=files
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_clean"] is True
        assert data["message"] == "The file is clean"


def test_scan_file_virus_detected(client_with_logged_in_user, monkeypatch):
    monkeypatch.setenv("AVSCAN_API_KEY", "test-key")
    monkeypatch.setenv("AVSCAN_API_URL", "https://test.example.com")

    # Mock the antivirus service
    async def mock_scan_file(self, file):
        return False, "Virus found: mail/dvh3v"

    with patch("services.antivirus.AntivirusService.scan_file", new=mock_scan_file):
        # Create a test file
        file_content = b"virus file content"
        files = {
            "file": ("virus.xlsx", BytesIO(file_content), "application/vnd.ms-excel")
        }

        response = client_with_logged_in_user.post(
            "/api/v1/antivirus/scan", files=files
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_clean"] is False
        assert "Virus found" in data["message"]


def test_scan_file_no_api_key(client_with_logged_in_user, monkeypatch):
    monkeypatch.delenv("AVSCAN_API_KEY", raising=False)
    monkeypatch.delenv("AVSCAN_API_URL", raising=False)

    # Mock the antivirus service
    async def mock_scan_file(self, file):
        return True, "Antivirus scanning disabled (no API key configured)"

    with patch("services.antivirus.AntivirusService.scan_file", new=mock_scan_file):
        # Create a test file
        file_content = b"test file content"
        files = {
            "file": ("test.xlsx", BytesIO(file_content), "application/vnd.ms-excel")
        }

        response = client_with_logged_in_user.post(
            "/api/v1/antivirus/scan", files=files
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_clean"] is True
        assert "disabled" in data["message"]


def test_scan_file_requires_authentication():
    client = TestClient(app)

    file_content = b"test file content"
    files = {"file": ("test.xlsx", BytesIO(file_content), "application/vnd.ms-excel")}

    response = client.post("/api/v1/antivirus/scan", files=files)

    assert response.status_code == 401
