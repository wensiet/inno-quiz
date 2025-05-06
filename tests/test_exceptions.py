"""Tests for exception handling utilities."""

from fastapi import HTTPException, Request
from starlette.responses import JSONResponse

from src.utils.exceptions import ErrorCode, http_exception_handler


def test_http_exception_handler():
    """Test http_exception_handler returns correct response format."""
    # Create a mock request
    mock_request = Request({"type": "http", "method": "GET", "path": "/test"})

    # Create a test exception
    test_exception = HTTPException(status_code=404, detail="Test not found")

    # Call the handler
    response = http_exception_handler(mock_request, test_exception)

    # Check response type
    assert isinstance(response, JSONResponse)

    # Check status code
    assert response.status_code == 404

    # Check content
    content = response.body.decode()
    assert "Test not found" in content
    assert "detail" in content


def test_error_code_unknown():
    """Test that ErrorCode returns UNKNOWN for invalid values."""
    # This tests the _missing_ method of ErrorCode

    # Access a non-existent code
    code = ErrorCode("NONEXISTENT_CODE")

    # It should return UNKNOWN
    assert code == ErrorCode.UNKNOWN
