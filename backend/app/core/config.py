import os
from pathlib import Path

from dotenv import load_dotenv


# Load project .env (root-level file) for local development and docker-compose.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def get_gemini_api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY")
