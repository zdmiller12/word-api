#!/usr/bin/env python3

import argparse

from scraper.nyt_cookie import refresh_nyt_cookie


def main() -> None:
    parser = argparse.ArgumentParser(prog="scraper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    nyt_cookie = subparsers.add_parser(
        "nyt-cookie",
        help="Refresh the NYT-S cookie and save it to a local JSON file.",
    )
    nyt_cookie.add_argument(
        "--cookie-out",
        default="~/.config/word-api/nyt_cookie.json",
        help="Path to write the NYT-S cookie JSON.",
    )
    nyt_cookie.add_argument(
        "--storage-state",
        default="~/.config/word-api/nyt_storage_state.json",
        help="Playwright storage state path for session reuse.",
    )
    nyt_cookie.add_argument(
        "--base-url",
        default="https://www.nytimes.com/crosswords",
        help="NYT page to open before reading cookies.",
    )
    nyt_cookie.add_argument(
        "--headful",
        action="store_true",
        help="Run with a visible browser window.",
    )
    nyt_cookie.add_argument(
        "--manual-login",
        action="store_true",
        help="Pause for manual login in the browser window.",
    )
    nyt_cookie.add_argument(
        "--timeout-ms",
        type=int,
        default=60000,
        help="Navigation timeout in milliseconds.",
    )
    nyt_cookie.add_argument(
        "--login",
        choices=["google", "none"],
        default="google",
        help="Login flow to use if NYT-S is missing.",
    )

    args = parser.parse_args()

    if args.command == "nyt-cookie":
        refresh_nyt_cookie(
            cookie_out=args.cookie_out,
            storage_state=args.storage_state,
            base_url=args.base_url,
            headful=args.headful,
            manual_login=args.manual_login,
            timeout_ms=args.timeout_ms,
            login_method=args.login,
        )


if __name__ == "__main__":
    main()
