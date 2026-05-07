"""Tests for word_api.models."""

from datetime import date, datetime
from pathlib import Path

import pytest

from word_api.models import (
    CluePair,
    DatasetRecord,
    Detail,
    LocalFile,
    PutPuzzleResponse,
    parse_date,
)


def test_parse_date_from_date() -> None:
    """parse_date returns date objects unchanged."""
    d = date(2024, 1, 1)
    assert parse_date(d) == d


def test_parse_date_from_datetime() -> None:
    """parse_date extracts the date from a datetime."""
    dt = datetime(2024, 6, 15, 12, 0, 0)
    assert parse_date(dt) == date(2024, 6, 15)


def test_parse_date_from_string() -> None:
    """parse_date parses an ISO date string."""
    assert parse_date("2024-03-20") == date(2024, 3, 20)


def test_parse_date_invalid() -> None:
    """parse_date raises ValueError for unparseable input."""
    with pytest.raises(ValueError, match="Unable to parse date"):
        parse_date("not-a-date")


def test_detail() -> None:
    """Detail model stores a detail string."""
    m = Detail(detail="something went wrong")
    assert m.detail == "something went wrong"


def test_local_file() -> None:
    """LocalFile stores md5sum and path."""
    m = LocalFile(md5sum="a" * 32, path=Path("/tmp/file.txt"))
    assert m.md5sum == "a" * 32
    assert m.path == Path("/tmp/file.txt")


def test_put_puzzle_response() -> None:
    """PutPuzzleResponse stores date, saved files, and source."""
    m = PutPuzzleResponse(
        date=date(2024, 1, 1),
        saved=[LocalFile(md5sum="c" * 32, path=Path("/tmp/x"))],
        source="nyt",
    )
    assert m.date == date(2024, 1, 1)
    assert m.source == "nyt"
    assert len(m.saved) == 1


def test_clue_pair() -> None:
    """CluePair stores all entry fields."""
    m = CluePair(number="1", direction="across", answer="CAT", clue="Feline", length=3)
    assert m.answer == "CAT"
    assert m.length == 3


def test_dataset_record() -> None:
    """DatasetRecord stores puzzle metadata and entries."""
    entry = CluePair(
        number="1", direction="across", answer="CAT", clue="Feline", length=3
    )
    m = DatasetRecord(
        date=date(2024, 1, 1),
        constructors=["Author"],
        editor="Editor",
        dimensions={"width": 15, "height": 15},
        entries=[entry],
    )
    assert m.source == "nyt"
    assert m.editor == "Editor"
    assert len(m.entries) == 1
