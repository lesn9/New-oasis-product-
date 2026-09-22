"""Configuration loader and validation."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Raised when required configuration is missing."""


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    alchemy_api_key: str
    log_level: str
    cache_ttl_seconds: int
    http_timeout_seconds: int
    max_concurrent_requests: int

    @classmethod
    def load(cls) -> "Config":
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        alchemy = os.getenv("ALCHEMY_API_KEY", "").strip()

        missing = []
        if not token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not alchemy:
            missing.append("ALCHEMY_API_KEY")

        if missing:
            raise ConfigError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return cls(
            telegram_bot_token=token,
            alchemy_api_key=alchemy,
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
            http_timeout_seconds=int(os.getenv("HTTP_TIMEOUT_SECONDS", "15")),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "10")),
        )


config = None


def get_config() -> Config:
    global config
    if config is None:
        config = Config.load()
    return config