"""Tests for word_api.util."""

import hashlib

import pytest

from word_api.util import get_md5sum_from_path


@pytest.mark.anyio
async def test_get_md5sum_from_path(tmp_path: object) -> None:
    """get_md5sum_from_path returns the correct MD5 hex digest."""
    content = b"hello world"
    f = tmp_path / "file.bin"  # type: ignore[operator]
    f.write_bytes(content)

    result = await get_md5sum_from_path(f)

    expected = hashlib.md5(content).hexdigest()
    assert result == expected
