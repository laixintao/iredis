import os
from pathlib import Path


__version__ = "1.0.1"


project_root = Path(os.path.dirname(os.path.abspath(__file__)))
project_data = project_root / "data"
