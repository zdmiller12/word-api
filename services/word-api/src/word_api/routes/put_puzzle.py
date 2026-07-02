"""PUT a new crossword puzzle into the domain of the word API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Request, status
from pydantic import BaseModel

from word_api.models import CrosswordSource, DateType, Detail, PutPuzzleResponse
from word_api.sources import nyt

router = APIRouter()


class PutPuzzleBody(BaseModel):
    """Request body for a put puzzle request."""

    source: CrosswordSource = "nyt"
    token: str | None = None


@router.put(
    "/puzzle/{date_}",
    response_model=PutPuzzleResponse,
    responses={
        status.HTTP_200_OK: {"model": PutPuzzleResponse},
        status.HTTP_400_BAD_REQUEST: {"model": Detail},
        status.HTTP_401_UNAUTHORIZED: {"model": Detail},
    },
    status_code=status.HTTP_200_OK,
)
async def put_puzzle(
    request: Request,
    date_: Annotated[
        DateType,
        Path(
            ...,
            description="Date of the puzzle to retrieve",
            examples=["2024-01-01"],
        ),
    ],
    body: Annotated[PutPuzzleBody, Body(default_factory=PutPuzzleBody)],
) -> PutPuzzleResponse:
    """Put a crossword puzzle into the domain of the Word API."""
    match body.source:
        case "nyt":
            token = body.token or request.cookies.get("NYT-S") or await nyt.get_token()
            if token is None:
                raise HTTPException(
                    status_code=401,
                    detail="NYT token must be provided in request body or as a cookie",
                )

            return await nyt.put_puzzle(date_=date_, token=token)
        case _:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported source: {body.source}",
            )
