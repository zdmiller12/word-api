#!/usr/bin/env python3
"""Main entry point for the scraper service."""

import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from word_api.routes import put_puzzle

app = FastAPI(
    title="Word API",
    version=os.getenv("WORD_API_GIT_SHA", "unknown")[:7],
)

app.include_router(put_puzzle.router)


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )
