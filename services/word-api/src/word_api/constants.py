"""Package constants."""

from pathlib import Path
from typing import Final

API_PATH: Final[Path] = Path.home() / ".local/share/word-api"
DATA_PATH: Final[Path] = API_PATH / "data"
BOARDS_PATH: Final[Path] = DATA_PATH / "boards"
PUZZLES_PATH: Final[Path] = DATA_PATH / "puzzles"
SOURCES_PATH: Final[Path] = API_PATH / "sources"
