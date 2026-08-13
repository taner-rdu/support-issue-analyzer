import os

from dotenv import load_dotenv

load_dotenv()


def get_secret(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise KeyError(f"Missing required environment variable: {name}")

    return value
