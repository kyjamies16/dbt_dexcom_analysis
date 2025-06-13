import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """
    Load the appropriate .env file based on ENV_MODE (dev/prod).
    Defaults to `.env` if not specified.
    """
    env_mode = os.getenv("ENV_MODE", "").lower() or "dev"
    print(f"[DEBUG] ENV_MODE={env_mode}")

    # Go two levels up: from utils/env.py → dexcom_dagster/ → dexcom/
    env_root = Path(__file__).resolve().parents[3]

    if env_mode in ("dev", "prod"):
        dotenv_path = env_root / f".env.{env_mode}"
    else:
        dotenv_path = env_root / ".env"

    if not dotenv_path.exists():
        raise FileNotFoundError(f"Expected .env file not found: {dotenv_path}")

    load_dotenv(dotenv_path=dotenv_path, override=True)

    return dotenv_path.name

