import tomllib
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal


@dataclass
class TelegramConfig:
    token: str
    allowed_ids: list[int]


@dataclass
class GeminiConfig:
    token: str
    model: str
    google_search_grounding: bool
    thinking_level: (
        Literal["low"]
        | Literal["medium"]
        | Literal["high"]
        | Literal["minimal"]
    )


@dataclass
class Settings:
    telegram: TelegramConfig
    gemini: GeminiConfig


def load_config(path: str) -> Settings:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return Settings(
        telegram=TelegramConfig(
            token=data["telegram"]["token"],
            allowed_ids=data["telegram"]["allowed_ids"],
        ),
        gemini=GeminiConfig(
            token=data["gemini"]["token"],
            model=data["gemini"]["model"],
            google_search_grounding=data["gemini"]["google-search-grounding"],
            thinking_level=data["gemini"]["thinking-level"],
        ),
    )


@lru_cache()
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    Returns:
        The application-wide ``Settings`` instance.
    """
    return load_config("config.toml")
