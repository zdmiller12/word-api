"""Tests for the PUT /puzzle/{date_} route."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from word_api.main import app
from word_api.routes.put_puzzle import PutPuzzleBody
from word_api.routes.put_puzzle import put_puzzle as put_puzzle_handler


def test_put_puzzle_with_body_token(put_puzzle_response):
    """Token in request body is used directly."""
    with (
        patch(
            "word_api.sources.nyt.put_puzzle",
            new=AsyncMock(return_value=put_puzzle_response),
        ),
        TestClient(app) as client,
    ):
        response = client.put("/puzzle/2024-01-01", json={"token": "body-token"})

    assert response.status_code == 200
    assert response.json()["source"] == "nyt"


def test_put_puzzle_with_cookie_token(put_puzzle_response):
    """NYT-S cookie is used when body token is absent."""
    with (
        patch(
            "word_api.sources.nyt.put_puzzle",
            new=AsyncMock(return_value=put_puzzle_response),
        ),
        TestClient(app) as client,
    ):
        response = client.put(
            "/puzzle/2024-01-01",
            json={},
            cookies={"NYT-S": "cookie-token"},
        )

    assert response.status_code == 200


def test_put_puzzle_with_file_token(put_puzzle_response):
    """Token from the .token file is used when body and cookie are absent."""
    with (
        patch(
            "word_api.sources.nyt.get_token", new=AsyncMock(return_value="file-token")
        ),
        patch(
            "word_api.sources.nyt.put_puzzle",
            new=AsyncMock(return_value=put_puzzle_response),
        ),
        TestClient(app) as client,
    ):
        response = client.put("/puzzle/2024-01-01", json={})

    assert response.status_code == 200


def test_put_puzzle_no_token_raises_401():
    """All token sources returning None yields a 401 response."""
    with (
        patch("word_api.sources.nyt.get_token", new=AsyncMock(return_value=None)),
        TestClient(app) as client,
    ):
        response = client.put("/puzzle/2024-01-01", json={})

    assert response.status_code == 401
    assert "token" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_put_puzzle_unknown_source_raises_400():
    """Unsupported source value raises a 400 HTTPException."""
    body = PutPuzzleBody.model_construct(source="unknown")
    request = MagicMock()
    request.cookies.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await put_puzzle_handler(request=request, date_=date(2024, 1, 1), body=body)

    assert exc_info.value.status_code == 400
    assert "unknown" in exc_info.value.detail
