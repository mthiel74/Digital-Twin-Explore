import sys
from pathlib import Path

# Ensure src/ is on path for test imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
