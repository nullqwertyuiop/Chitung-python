from pathlib import Path
from typing import Final

CHITUNG_ROOT: Final[Path] = Path(__file__).parent.parent.resolve()
PROJECT_ROOT: Final[Path] = CHITUNG_ROOT.parent.resolve()
DATA_ROOT: Final[Path] = CHITUNG_ROOT / "data"
ASSETS_ROOT: Final[Path] = CHITUNG_ROOT / "assets"
