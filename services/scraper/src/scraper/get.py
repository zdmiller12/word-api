"""Module for getting crossword data."""

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import requests

import scraper.constants as ct


@dataclass(frozen=True)
class GetConfig:
    """Configuration for getting a crossword puzzle."""

    date_: date
    source: ct.CrosswordSource

    token: str | None = None

    def get_token(self) -> str:
        """Get API token from the config or token file."""
        return self.token or self.token_path.read_text().strip()

    @property
    def puzzles_parent(self) -> Path:
        """Parent directory for puzzles."""
        return ct.SOURCES_PATH / self.source / "data/puzzles"

    @property
    def puzzle_path(self) -> Path:
        """Path to the puzzle data file."""
        return (
            self.puzzles_parent
            / str(self.date_.year)
            / str(self.date_.month).zfill(2)
            / str(self.date_.day).zfill(2)
            / "daily-puzzle.json"
        )

    @property
    def token_path(self) -> Path:
        """Path to the token file."""
        return ct.SOURCES_PATH / self.source / ".token"


def get_nyt(cfg: GetConfig) -> requests.Response:
    """Get a NYT crossworld puzzle as JSON."""
    date_str = cfg.date_.strftime("%Y-%m-%d")
    return requests.get(
        f"https://www.nytimes.com/svc/crosswords/v6/puzzle/daily/{date_str}.json",
        cookies={"NYT-S": cfg.get_token()},
        headers={"Accept": "application/json"},
    )


def get(cfg: GetConfig) -> None:
    """Retrieve a crossword puzzle based on the provided configuration."""
    if cfg.source == "nyt":
        response = get_nyt(cfg)
    else:
        raise ValueError(f"Unsupported source: {cfg.source}")

    response.raise_for_status()
    cfg.puzzle_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.puzzle_path.write_text(json.dumps(response.json(), indent=2))
    print(f"Saved {cfg.puzzle_path=}")
