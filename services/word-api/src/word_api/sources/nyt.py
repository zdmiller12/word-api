"""Crossword source: New York Times."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING

import aiofiles
import httpx
from lxml import etree

from word_api import constants as ct
from word_api.models import LocalFile, PutPuzzleResponse
from word_api.util import get_md5sum_from_path

if TYPE_CHECKING:
    from datetime import date


async def _get_puzzle(date_: date, token: str) -> httpx.Response:
    """Get a crossword puzzle from the New York Times."""
    async with httpx.AsyncClient() as session:
        return await session.get(
            f"https://www.nytimes.com/svc/crosswords/v6/puzzle/daily/{date_.isoformat()}.json",
            cookies={"NYT-S": token},
            headers={"Accept": "application/json"},
        )


async def get_puzzle(date_: date, token: str) -> dict:
    """Safely get a crossword puzzle from the New York Times."""
    response = await _get_puzzle(date_=date_, token=token)
    response.raise_for_status()
    return response.json()


async def get_token() -> str:
    """Read NYT token from file."""
    token_path = ct.SOURCES_PATH / "nyt" / ".token"
    async with aiofiles.open(token_path) as f:
        return (await f.read()).strip()


async def put_puzzle(date_: date, token: str) -> PutPuzzleResponse:
    """Put a crossword puzzle from the New York Times into the Word API."""
    puzzle = await get_puzzle(date_=date_, token=token)
    board_out, puzzle_out = await asyncio.gather(
        save_board(date_=date_, puzzle=puzzle),
        save_puzzle(date_=date_, puzzle=puzzle),
    )
    return PutPuzzleResponse(
        date=date_,
        saved=[
            LocalFile(
                md5sum=await get_md5sum_from_path(board_out),
                path=board_out,
            ),
            LocalFile(
                md5sum=await get_md5sum_from_path(puzzle_out),
                path=puzzle_out,
            ),
        ],
        source="nyt",
    )


async def save_board(date_: date, puzzle: dict) -> Path:
    """Write the board of a NYT puzzle to an SVG file."""
    board_out = (
        ct.BOARDS_PATH
        / "source=nyt"
        / f"year={date_.year}"
        / f"month={str(date_.month).zfill(2)}"
        / f"day={str(date_.day).zfill(2)}"
        / "board.svg"
    )
    board_out.parent.mkdir(parents=True, exist_ok=True)

    root = etree.fromstring(puzzle["body"][0]["board"])
    etree.indent(root, space="  ", level=0)
    async with aiofiles.open(board_out, "w") as f:
        await f.write(etree.tostring(root, encoding="unicode"))
    return board_out


async def save_puzzle(date_: date, puzzle: dict) -> Path:
    """Write the puzzle data of a NYT puzzle to a JSON file."""
    puzzle_out = (
        ct.PUZZLES_PATH
        / "source=nyt"
        / f"year={date_.year}"
        / f"month={str(date_.month).zfill(2)}"
        / f"day={str(date_.day).zfill(2)}"
        / "puzzle.json"
    )
    puzzle_out.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(puzzle_out, "w") as f:
        await f.write(json.dumps(puzzle, indent=2))

    return puzzle_out
