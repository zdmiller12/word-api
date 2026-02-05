"""Package constants."""

from pathlib import Path
from typing import Final, Literal

CrosswordSource = Literal["nyt"]

DATA_PATH: Final[Path] = Path.home() / ".local/share/word-api"
SOURCES_PATH: Final[Path] = DATA_PATH / "sources"
