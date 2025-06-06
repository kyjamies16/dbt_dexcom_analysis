# utils/load_env.py

from pathlib import Path
import sys
from dotenv import load_dotenv

def load_root_env():
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    load_dotenv()