"""GET a streaming JSONL dataset of crossword entries for agent training."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from datetime import date
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from word_api import constants as ct
from word_api.models import DatasetRecord, DateType
from word_api.sources import nyt

logger = logging.getLogger(__name__)
router = APIRouter()


async def _iter_records(
    date_from: date | None,
    date_to: date | None,
) -> AsyncIterator[DatasetRecord]:
    """Yield a DatasetRecord for each saved puzzle within the date range."""
    paths = sorted(ct.PUZZLES_PATH.glob("source=nyt/year=*/month=*/day=*/puzzle.json"))
    for path in paths:
        parts = {
            seg.split("=")[0]: seg.split("=")[1] for seg in path.parts if "=" in seg
        }
        try:
            puzzle_date = date(
                int(parts["year"]), int(parts["month"]), int(parts["day"])
            )
        except (KeyError, ValueError):
            logger.warning("Could not parse date from path: %s", path)
            continue

        if date_from and puzzle_date < date_from:
            continue
        if date_to and puzzle_date > date_to:
            continue

        try:
            async with aiofiles.open(path) as f:
                puzzle = json.loads(await f.read())
            yield nyt.extract_dataset_record(date_=puzzle_date, puzzle=puzzle)
        except Exception:
            logger.warning("Failed to extract record from %s", path, exc_info=True)


@router.get(
    "/dataset",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"application/x-ndjson": {}},
            "description": "Streaming JSONL — one puzzle record per line",
        }
    },
)
async def get_dataset(
    date_from: Annotated[
        DateType | None,
        Query(description="Start date, inclusive (e.g. 2024-01-01)"),
    ] = None,
    date_to: Annotated[
        DateType | None,
        Query(description="End date, inclusive (e.g. 2024-12-31)"),
    ] = None,
) -> StreamingResponse:
    """Stream a JSONL dataset of crossword puzzles extracted from saved NYT files.

    Each line is a JSON object matching the DatasetRecord schema:
    - date, constructors, editor, dimensions
    - entries: list of {number, direction, answer, clue, length}

    """

    async def generate() -> AsyncIterator[str]:
        async for record in _iter_records(date_from=date_from, date_to=date_to):
            yield record.model_dump_json() + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
