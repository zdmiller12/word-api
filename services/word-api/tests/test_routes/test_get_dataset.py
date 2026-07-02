"""Tests for the GET /dataset route."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from word_api.main import app
from word_api.routes import get_dataset


def _write_puzzle(  # noqa: PLR0913
    base: Path,
    year: str,
    month: str,
    day: str,
    content,
    source: str = "nyt",
):
    """Write a puzzle.json under source=nyt/year=/month=/day= inside base."""
    path = base / f"year={year}/month={month}/day={day}/source={source}/puzzle.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        path.write_text(content)
    else:
        path.write_text(json.dumps(content))


def test_get_dataset_empty(monkeypatch, tmp_path):
    """No puzzle files → empty response body."""
    monkeypatch.setattr(get_dataset, "PUZZLES_PATH", tmp_path)

    with TestClient(app) as client:
        response = client.get("/dataset")

    assert response.status_code == 200
    assert response.text == ""


def test_get_dataset_success(minimal_puzzle, monkeypatch, tmp_path):
    """Valid puzzle files are streamed as JSONL lines."""
    monkeypatch.setattr(get_dataset, "PUZZLES_PATH", tmp_path)
    _write_puzzle(tmp_path, "2024", "01", "01", minimal_puzzle)
    _write_puzzle(tmp_path, "2024", "01", "02", minimal_puzzle)

    with TestClient(app) as client:
        response = client.get("/dataset")

    lines = [ln for ln in response.text.strip().splitlines() if ln]
    assert len(lines) == 2
    record = json.loads(lines[0])
    assert record["source"] == "nyt"
    assert record["date"] == "2024-01-01"
    assert len(record["entries"]) == 4


def test_get_dataset_date_from_filter(minimal_puzzle, monkeypatch, tmp_path):
    """Puzzles before date_from are excluded."""
    monkeypatch.setattr(get_dataset, "PUZZLES_PATH", tmp_path)
    _write_puzzle(tmp_path, "2024", "01", "01", minimal_puzzle)
    _write_puzzle(tmp_path, "2024", "01", "02", minimal_puzzle)

    with TestClient(app) as client:
        response = client.get("/dataset?date_from=2024-01-02")

    lines = [ln for ln in response.text.strip().splitlines() if ln]
    assert len(lines) == 1
    assert json.loads(lines[0])["date"] == "2024-01-02"


def test_get_dataset_date_to_filter(minimal_puzzle, monkeypatch, tmp_path):
    """Puzzles after date_to are excluded."""
    monkeypatch.setattr(get_dataset, "PUZZLES_PATH", tmp_path)
    _write_puzzle(tmp_path, "2024", "01", "01", minimal_puzzle)
    _write_puzzle(tmp_path, "2024", "01", "02", minimal_puzzle)

    with TestClient(app) as client:
        response = client.get("/dataset?date_to=2024-01-01")

    lines = [ln for ln in response.text.strip().splitlines() if ln]
    assert len(lines) == 1
    assert json.loads(lines[0])["date"] == "2024-01-01"


def test_get_dataset_bad_path(monkeypatch, tmp_path):
    """Paths with non-integer date segments are skipped with a warning."""
    monkeypatch.setattr(get_dataset, "PUZZLES_PATH", tmp_path)
    _write_puzzle(tmp_path, "abc", "01", "01", "{}")

    with TestClient(app) as client:
        response = client.get("/dataset")

    assert response.text == ""


def test_get_dataset_corrupt_file(monkeypatch, tmp_path):
    """Files with invalid JSON are skipped with a warning."""
    monkeypatch.setattr(get_dataset, "PUZZLES_PATH", tmp_path)
    _write_puzzle(tmp_path, "2024", "01", "01", "not valid json {{{")

    with TestClient(app) as client:
        response = client.get("/dataset")

    assert response.text == ""
