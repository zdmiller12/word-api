"""Tests for word_api.sources.nyt."""

import json
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

import word_api.constants as ct
from word_api.sources import nyt


@pytest.mark.anyio
async def test_get_puzzle_success(minimal_puzzle: dict) -> None:
    """get_puzzle fetches the correct URL and returns parsed JSON."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = minimal_puzzle

    with patch("httpx.AsyncClient") as mock_client:
        inst = mock_client.return_value
        inst.__aenter__ = AsyncMock(return_value=inst)
        inst.__aexit__ = AsyncMock(return_value=None)
        inst.get = AsyncMock(return_value=mock_response)

        result = await nyt.get_puzzle(date_=date(2024, 1, 1), token="tok")

    assert result == minimal_puzzle
    inst.get.assert_called_once_with(
        "https://www.nytimes.com/svc/crosswords/v6/puzzle/daily/2024-01-01.json",
        cookies={"NYT-S": "tok"},
        headers={"Accept": "application/json"},
    )


@pytest.mark.anyio
async def test_get_puzzle_http_error() -> None:
    """get_puzzle propagates HTTP errors from raise_for_status."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized", request=MagicMock(), response=MagicMock()
    )

    with patch("httpx.AsyncClient") as mock_client:
        inst = mock_client.return_value
        inst.__aenter__ = AsyncMock(return_value=inst)
        inst.__aexit__ = AsyncMock(return_value=None)
        inst.get = AsyncMock(return_value=mock_response)

        with pytest.raises(httpx.HTTPStatusError):
            await nyt.get_puzzle(date_=date(2024, 1, 1), token="bad")


@pytest.mark.anyio
async def test_get_token(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> None:
    """get_token reads and strips the token from the .token file."""
    token_dir = tmp_path / "nyt"  # type: ignore[operator]
    token_dir.mkdir()
    (token_dir / ".token").write_text("secret-token\n")

    monkeypatch.setattr(ct, "SOURCES_PATH", tmp_path)

    result = await nyt.get_token()
    assert result == "secret-token"


@pytest.mark.anyio
async def test_save_board(
    minimal_puzzle: dict, tmp_path: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    """save_board writes an indented SVG to the expected path."""
    monkeypatch.setattr(ct, "BOARDS_PATH", tmp_path)

    result = await nyt.save_board(date_=date(2024, 1, 1), puzzle=minimal_puzzle)

    expected = (
        tmp_path / "source=nyt" / "year=2024" / "month=01" / "day=01" / "board.svg"
    )  # type: ignore[operator]
    assert result == expected
    assert expected.exists()
    assert "<svg" in expected.read_text()


@pytest.mark.anyio
async def test_save_puzzle(
    minimal_puzzle: dict, tmp_path: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    """save_puzzle writes the puzzle JSON to the expected path."""
    monkeypatch.setattr(ct, "PUZZLES_PATH", tmp_path)

    result = await nyt.save_puzzle(date_=date(2024, 1, 1), puzzle=minimal_puzzle)

    expected = (
        tmp_path / "source=nyt" / "year=2024" / "month=01" / "day=01" / "puzzle.json"
    )  # type: ignore[operator]
    assert result == expected
    assert expected.exists()
    saved = json.loads(expected.read_text())
    assert saved["constructors"] == ["Test Author"]


@pytest.mark.anyio
async def test_put_puzzle(minimal_puzzle: dict, tmp_path: object) -> None:
    """put_puzzle composes sub-functions and returns a PutPuzzleResponse."""
    board_path = tmp_path / "board.svg"  # type: ignore[operator]
    puzzle_path = tmp_path / "puzzle.json"  # type: ignore[operator]

    with (
        patch(
            "word_api.sources.nyt.get_puzzle",
            new=AsyncMock(return_value=minimal_puzzle),
        ),
        patch(
            "word_api.sources.nyt.save_board", new=AsyncMock(return_value=board_path)
        ),
        patch(
            "word_api.sources.nyt.save_puzzle", new=AsyncMock(return_value=puzzle_path)
        ),
        patch(
            "word_api.sources.nyt.get_md5sum_from_path",
            new=AsyncMock(side_effect=["a" * 32, "b" * 32]),
        ),
    ):
        result = await nyt.put_puzzle(date_=date(2024, 1, 1), token="tok")

    assert result.source == "nyt"
    assert result.date == date(2024, 1, 1)
    assert len(result.saved) == 2
    assert result.saved[0].md5sum == "a" * 32
    assert result.saved[1].md5sum == "b" * 32


def test_extract_dataset_record(minimal_puzzle: dict) -> None:
    """extract_dataset_record converts a puzzle dict to a DatasetRecord."""
    record = nyt.extract_dataset_record(date_=date(2024, 1, 1), puzzle=minimal_puzzle)

    assert record.source == "nyt"
    assert record.date == date(2024, 1, 1)
    assert record.constructors == ["Test Author"]
    assert record.editor == "Test Editor"
    assert record.dimensions == {"width": 3, "height": 1}
    assert len(record.entries) == 4

    across = record.entries[0]
    assert across.number == "1"
    assert across.direction == "across"
    assert across.answer == "CAT"
    assert across.clue == "Feline"
    assert across.length == 3
