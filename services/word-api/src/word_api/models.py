"""General models for the word API."""

from datetime import date, datetime
from pathlib import Path
from typing import Annotated, Any, Literal

from dateutil import parser
from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer


def parse_date(value: Any) -> date:
    """Try parsing date from value."""
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return parser.parse(value).date()
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Unable to parse date from {value=}") from exc


type DateType = Annotated[
    date,
    BeforeValidator(parse_date),
    PlainSerializer(
        lambda d: d.isoformat(),
        return_type=str,
        when_used="json",
    ),
]
type Md5SumType = Annotated[str, Field(pattern=r"^[a-fA-F0-9]{32}$")]


class Detail(BaseModel):
    """Model with details."""

    detail: str


class LocalFile(BaseModel):
    """Model representing a local file."""

    md5sum: Md5SumType
    path: Path


class PutPuzzleResponse(BaseModel):
    """Response payload for a put puzzle request."""

    date: DateType
    saved: list[LocalFile]
    source: Literal["nyt"] = "nyt"
