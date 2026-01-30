import json
import os
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from playwright.sync_api import sync_playwright


@dataclass(frozen=True)
class NytCookie:
    name: str
    value: str
    domain: str
    path: str
    expires: float | None


def refresh_nyt_cookie(
    *,
    cookie_out: str,
    storage_state: str,
    base_url: str,
    headful: bool,
    manual_login: bool,
    timeout_ms: int,
    login_method: str,
) -> None:
    cookie_path = Path(cookie_out).expanduser()
    storage_state_path = Path(storage_state).expanduser()
    _ensure_private_dir(cookie_path.parent)
    _ensure_private_dir(storage_state_path.parent)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not headful)
        context = browser.new_context(
            storage_state=str(storage_state_path)
            if storage_state_path.exists()
            else None
        )
        page = context.new_page()

        page.goto(base_url, wait_until="domcontentloaded", timeout=timeout_ms)
        cookie = _find_cookie(context, "NYT-S")

        if cookie is None and login_method == "google":
            if manual_login:
                _manual_login_flow(page, timeout_ms)
            else:
                _google_login_flow(page, timeout_ms)
            cookie = _wait_for_cookie(context, "NYT-S", timeout_ms=timeout_ms)

        if cookie is None:
            raise RuntimeError(
                "NYT-S cookie not found. Try --headful --manual-login or provide "
                "GOOGLE_EMAIL and GOOGLE_PASSWORD env vars."
            )

        context.storage_state(path=str(storage_state_path))
        _write_cookie(cookie_path, cookie)
        browser.close()


def _manual_login_flow(page, timeout_ms: int) -> None:
    page.goto(
        "https://myaccount.nytimes.com/auth/login?redirect_uri=https://www.nytimes.com/crosswords",
        wait_until="domcontentloaded",
        timeout=timeout_ms,
    )
    input("Complete NYT login in the browser window, then press Enter here...")


def _google_login_flow(page, timeout_ms: int) -> None:
    email = os.environ.get("GOOGLE_EMAIL")
    password = os.environ.get("GOOGLE_PASSWORD")
    if not email or not password:
        raise RuntimeError(
            "GOOGLE_EMAIL and GOOGLE_PASSWORD must be set for automated Google login."
        )

    page.goto(
        "https://myaccount.nytimes.com/auth/login?redirect_uri=https://www.nytimes.com/crosswords",
        wait_until="domcontentloaded",
        timeout=timeout_ms,
    )

    google_button = page.get_by_role("button", name=re.compile("google", re.I))
    google_button.click(timeout=timeout_ms)

    _fill_if_visible(page, "input[type='email']", email, timeout_ms)
    _click_if_visible(page, "button:has-text('Next')", timeout_ms)

    _fill_if_visible(page, "input[type='password']", password, timeout_ms)
    _click_if_visible(page, "button:has-text('Next')", timeout_ms)


def _fill_if_visible(page, selector: str, value: str, timeout_ms: int) -> None:
    locator = page.locator(selector)
    locator.wait_for(state="visible", timeout=timeout_ms)
    locator.fill(value)


def _click_if_visible(page, selector: str, timeout_ms: int) -> None:
    locator = page.locator(selector)
    locator.wait_for(state="visible", timeout=timeout_ms)
    locator.click()


def _wait_for_cookie(
    context,
    name: str,
    *,
    timeout_ms: int,
    poll_interval: float = 1.0,
) -> NytCookie | None:
    deadline = time.time() + (timeout_ms / 1000)
    while time.time() < deadline:
        cookie = _find_cookie(context, name)
        if cookie is not None:
            return cookie
        time.sleep(poll_interval)
    return None


def _find_cookie(context, name: str) -> NytCookie | None:
    for cookie in context.cookies():
        if cookie.get("name") == name:
            return NytCookie(
                name=cookie["name"],
                value=cookie["value"],
                domain=cookie.get("domain", ""),
                path=cookie.get("path", "/"),
                expires=cookie.get("expires") or None,
            )
    return None


def _write_cookie(path: Path, cookie: NytCookie) -> None:
    payload = asdict(cookie) | {"retrieved_at": time.time()}
    tmp_path = path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp_path, path)
    os.chmod(path, 0o600)


def _ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
