import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")
ENVIRONMENT = os.getenv("ENVIRONMENT")
print(f"Environment: {ENVIRONMENT}")
if ENVIRONMENT is not None and str(ENVIRONMENT).lower() not in ["dev", "test"]:
    raise ValueError("env variable ENVIRONMENT must be dev or test")

DEFAULT_CONFIG_FILE = (
    "_".join(x.lower() for x in ["config", ENVIRONMENT] if x is not None) + ".yaml"
)
DEFAULT_SECRETS_DIR = "secrets/"


class LogLevel(str, Enum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"


class Log(BaseModel):
    level: LogLevel
    format: str | None = "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"

    model_config = SettingsConfigDict(use_enum_values=True)


class Engine(str, Enum):
    sqlite = "sqlite"
    oracle = "oracle"
    mysql = "mysql"


class Database(BaseModel):
    engine: Engine
    dsn: str | None
    username: str | None = None
    password: str | None = None

    model_config = SettingsConfigDict(use_enum_values=True)


class Config(YamlBaseSettings):
    name: str
    log: Log
    database: Database

    model_config = SettingsConfigDict(  # type: ignore[typeddict-unknown-key]
        env_nested_delimiter="__",
        use_enum_values=True,
        yaml_file=os.getenv("APP_CONFIG")
        or (Path(__file__).parent.parent / DEFAULT_CONFIG_FILE),
        secrets_dir=os.getenv("APP_SECRETS")
        or (Path(__file__).parent.parent / DEFAULT_SECRETS_DIR),
    )


_config: Config = Config()


def get_config() -> Config:
    assert _config is not None, "Config is empty!"
    return _config


def scramble_secret(secret: str | None) -> str:
    if secret is None:
        return ""
    return f"{secret[:3]}***{secret[-3:]}"
