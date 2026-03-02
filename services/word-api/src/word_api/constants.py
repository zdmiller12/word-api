"""Package constants."""

from pathlib import Path
from typing import Final, Literal

CrosswordSource = Literal["nyt"]

DATA_PATH: Final[Path] = Path.home() / ".local/share/word-api"
BOARDS_PATH: Final[Path] = DATA_PATH / "boards"
PUZZLES_PATH: Final[Path] = DATA_PATH / "puzzles"
SOURCES_PATH: Final[Path] = DATA_PATH / "sources"
