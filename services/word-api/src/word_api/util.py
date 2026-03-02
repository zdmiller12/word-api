"""General utility functions."""

import hashlib
from pathlib import Path

import aiofiles


async def get_md5sum_from_path(path: Path | str, chunk_size_bytes: int = 8192) -> str:
    """Get MD5sum from file at path."""
    md5_hash = hashlib.md5()
    async with aiofiles.open(path, "rb") as file:
        while chunk := await file.read(chunk_size_bytes):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
