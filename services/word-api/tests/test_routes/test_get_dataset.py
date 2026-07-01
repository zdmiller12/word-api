"""Tests for the GET /dataset route."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import word_api.constants as ct
from word_api.main import app


def _write_puzzle(base: Path, year: str, month: str, day: str, content: object) -> None:
    """Write a puzzle.json under source=nyt/year=/month=/day= inside base."""
    path = base / f"source=nyt/year={year}/month={month}/day={day}/puzzle.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        path.write_text(content)
    else:
        path.write_text(json.dumps(content))


def test_get_dataset_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No puzzle files → empty response body."""
    monkeypatch.setattr(ct, "PUZZLES_PATH", tmp_path)

    with TestClient(app) as client:
        response = client.get("/dataset")

    assert response.status_code == 200
    assert response.text == ""


def test_get_dataset_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, minimal_puzzle: dict
) -> None:
    """Valid puzzle files are streamed as JSONL lines."""
    monkeypatch.setattr(ct, "PUZZLES_PATH", tmp_path)
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


def test_get_dataset_date_from_filter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, minimal_puzzle: dict
) -> None:
    """Puzzles before date_from are excluded."""
    monkeypatch.setattr(ct, "PUZZLES_PATH", tmp_path)
    _write_puzzle(tmp_path, "2024", "01", "01", minimal_puzzle)
    _write_puzzle(tmp_path, "2024", "01", "02", minimal_puzzle)

    with TestClient(app) as client:
        response = client.get("/dataset?date_from=2024-01-02")

    lines = [ln for ln in response.text.strip().splitlines() if ln]
    assert len(lines) == 1
    assert json.loads(lines[0])["date"] == "2024-01-02"


def test_get_dataset_date_to_filter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, minimal_puzzle: dict
) -> None:
    """Puzzles after date_to are excluded."""
    monkeypatch.setattr(ct, "PUZZLES_PATH", tmp_path)
    _write_puzzle(tmp_path, "2024", "01", "01", minimal_puzzle)
    _write_puzzle(tmp_path, "2024", "01", "02", minimal_puzzle)

    with TestClient(app) as client:
        response = client.get("/dataset?date_to=2024-01-01")

    lines = [ln for ln in response.text.strip().splitlines() if ln]
    assert len(lines) == 1
    assert json.loads(lines[0])["date"] == "2024-01-01"


def test_get_dataset_bad_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Paths with non-integer date segments are skipped with a warning."""
    monkeypatch.setattr(ct, "PUZZLES_PATH", tmp_path)
    _write_puzzle(tmp_path, "abc", "01", "01", "{}")

    with TestClient(app) as client:
        response = client.get("/dataset")

    assert response.text == ""


def test_get_dataset_corrupt_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Files with invalid JSON are skipped with a warning."""
    monkeypatch.setattr(ct, "PUZZLES_PATH", tmp_path)
    _write_puzzle(tmp_path, "2024", "01", "01", "not valid json {{{")

    with TestClient(app) as client:
        response = client.get("/dataset")

    assert response.text == ""
