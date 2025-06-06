import sys
from pathlib import Path

# Ensure project root is in sys.path so aurora_memory can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
