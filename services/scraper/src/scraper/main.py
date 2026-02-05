#!/usr/bin/env python3
"""Main entry point for the scraper service."""

import argparse
from datetime import date
from typing import get_args

from dateutil import parser

import scraper.constants as ct
from scraper import get


def _parse_date(date_str: str) -> date:
    """Parse a date string into a date object."""
    return parser.parse(date_str).date()


def main() -> None:
    """Run CLI."""
    parser = argparse.ArgumentParser(prog="scraper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_cmd = subparsers.add_parser(
        "get",
        help="Retrieve a crossword puzzle.",
    )
    get_cmd.add_argument(
        "-d",
        "--date",
        help="Date of the puzzle to retrieve (YYYY-MM-DD).",
        required=True,
        type=_parse_date,
    )
    get_cmd.add_argument(
        "-s",
        "--source",
        choices=get_args(ct.CrosswordSource),
        default="nyt",
        help="Source of the crossword puzzle.",
    )
    get_cmd.add_argument(
        "-t",
        "--token",
        help="API token for getting crossword data.",
        required=False,
    )

    args = parser.parse_args()

    if args.command == "get":
        get.get(
            get.GetConfig(
                date_=args.date,
                source=args.source,
                token=args.token,
            )
        )


if __name__ == "__main__":
    main()
