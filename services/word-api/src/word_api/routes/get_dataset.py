"""GET a streaming JSONL dataset of crossword entries for agent training."""

from __future__ import annotations

import itertools
import json
import logging
from collections.abc import AsyncIterator, Iterable
from datetime import date
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Query, status
from fastapi.responses import StreamingResponse

from word_api.constants import PUZZLES_PATH
from word_api.models import CrosswordSource, DatasetRecord, DateType
from word_api.sources import nyt

logger = logging.getLogger(__name__)
router = APIRouter()


async def _iter_records(
    date_from: date | None,
    date_to: date | None,
    sources: Iterable[str] | None = None,
) -> AsyncIterator[DatasetRecord]:
    """Yield a DatasetRecord for each saved puzzle within the date range."""
    sources = sources or ["nyt"]
    paths = sorted(
        itertools.chain.from_iterable(
            PUZZLES_PATH.glob(f"year=*/month=*/day=*/source={source}/puzzle.json")
            for source in sources
        )
    )
    for path in paths:
        parts = {
            seg.split("=")[0]: seg.split("=")[1] for seg in path.parts if "=" in seg
        }
        try:
            puzzle_date = date(
                int(parts["year"]),
                int(parts["month"]),
                int(parts["day"]),
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
        status.HTTP_200_OK: {
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
    sources: Annotated[
        Iterable[CrosswordSource] | None,
        Query(description="Sources to include in the dataset"),
    ] = None,
) -> StreamingResponse:
    """Stream a JSONL dataset of crossword puzzles extracted from saved NYT files.

    Each line is a JSON object matching the DatasetRecord schema:
    - date, constructors, editor, dimensions
    - entries: list of {number, direction, answer, clue, length}

    """

    async def generate() -> AsyncIterator[str]:
        async for record in _iter_records(
            date_from=date_from,
            date_to=date_to,
            sources=sources,
        ):
            yield record.model_dump_json() + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
