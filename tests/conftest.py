"""Make the modules in src/ importable as `import parser`, `import cli`, ..."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
