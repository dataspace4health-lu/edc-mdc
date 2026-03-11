from fastapi import Request
from auth.jwt_helpers import extract_bearer_token


def test_extract_bearer_token_success():
    mock_request = Request(
        {
            "type": "http",
            "headers": [(b"authorization", b"Bearer test-token-123")],
        }
    )
    token = extract_bearer_token(mock_request)
    assert token == "test-token-123"


def test_extract_bearer_token_no_header():
    mock_request = Request({"type": "http", "headers": []})
    token = extract_bearer_token(mock_request)
    assert token is None


def test_extract_bearer_token_wrong_scheme():
    mock_request = Request(
        {"type": "http", "headers": [(b"authorization", b"Basic test-token-123")]}
    )
    token = extract_bearer_token(mock_request)
    assert token is None


def test_extract_bearer_token_empty_token():
    mock_request = Request(
        {"type": "http", "headers": [(b"authorization", b"Bearer ")]}
    )
    token = extract_bearer_token(mock_request)
    assert token is None


def test_extract_bearer_token_with_whitespace():
    mock_request = Request(
        {"type": "http", "headers": [(b"authorization", b"Bearer  token-with-space  ")]}
    )
    token = extract_bearer_token(mock_request)
    assert token == "token-with-space"
