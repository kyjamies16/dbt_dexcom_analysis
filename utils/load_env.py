from pathlib import Path
from dotenv import load_dotenv

def load_root_env():
    root_path = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=root_path / ".env")
