"""Shared fixtures for word-api tests."""

from datetime import date
from pathlib import Path

import pytest

from word_api.models import LocalFile, PutPuzzleResponse

MINIMAL_SVG = '<svg xmlns="http://www.w3.org/2000/svg"/>'

MINIMAL_PUZZLE: dict = {
    "body": [
        {
            "board": MINIMAL_SVG,
            "cells": [
                {"answer": "C", "clues": [0, 1], "label": "1", "type": 1},
                {"answer": "A", "clues": [0, 2], "label": "2", "type": 1},
                {"answer": "T", "clues": [0, 3], "label": "3", "type": 1},
            ],
            "clues": [
                {
                    "cells": [0, 1, 2],
                    "direction": "Across",
                    "label": "1",
                    "text": [{"plain": "Feline"}],
                },
                {
                    "cells": [0],
                    "direction": "Down",
                    "label": "1",
                    "text": [{"plain": "Letter"}],
                },
                {
                    "cells": [1],
                    "direction": "Down",
                    "label": "2",
                    "text": [{"plain": "Article"}],
                },
                {
                    "cells": [2],
                    "direction": "Down",
                    "label": "3",
                    "text": [{"plain": "Another"}],
                },
            ],
            "clueLists": [],
            "dimensions": {"width": 3, "height": 1},
        }
    ],
    "constructors": ["Test Author"],
    "editor": "Test Editor",
    "publicationDate": "2024-01-01",
    "copyright": "Test",
    "id": 1,
    "lastUpdated": "2024-01-01",
    "relatedContent": [],
}


@pytest.fixture
def minimal_puzzle() -> dict:
    """Return a minimal valid NYT puzzle dict."""
    return MINIMAL_PUZZLE


@pytest.fixture
def put_puzzle_response() -> PutPuzzleResponse:
    """Return a minimal PutPuzzleResponse."""
    return PutPuzzleResponse(
        date=date(2024, 1, 1),
        saved=[
            LocalFile(md5sum="a" * 32, path=Path("/tmp/board.svg")),
            LocalFile(md5sum="b" * 32, path=Path("/tmp/puzzle.json")),
        ],
        source="nyt",
    )
