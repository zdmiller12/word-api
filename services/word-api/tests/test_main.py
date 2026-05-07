"""Tests for word_api.main (app-level behaviour)."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from word_api.main import app


def test_generic_exception_handler() -> None:
    """Unhandled exceptions from route handlers return a 500 JSON response."""
    with (
        patch(
            "word_api.sources.nyt.put_puzzle",
            new=AsyncMock(side_effect=RuntimeError("something broke")),
        ),
        TestClient(app, raise_server_exceptions=False) as client,
    ):
        response = client.put("/puzzle/2024-01-01", json={"token": "tok"})

    assert response.status_code == 500
    assert response.json() == {"detail": "something broke"}
