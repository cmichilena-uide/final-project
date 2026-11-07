from pathlib import Path

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
SQLITE_PREFIX = "sqlite:///"


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    database_url: str = Field(min_length=1)
    secret_key: str = Field(min_length=32)
    algorithm: str = Field(min_length=1)
    access_token_expire_minutes: int = Field(gt=0)
    cors_origins: list[str] = Field(min_length=1)
    admin_email: EmailStr
    admin_password: str = Field(min_length=8)

    @field_validator("database_url")
    @classmethod
    def anchor_sqlite_path(cls, value: str) -> str:
        if value.startswith(SQLITE_PREFIX):
            path = Path(value.removeprefix(SQLITE_PREFIX))
            if not path.is_absolute():
                return f"{SQLITE_PREFIX}{BASE_DIR / path}"
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


def load_settings() -> Settings:
    values = dotenv_values(ENV_FILE)
    return Settings.model_validate(
        {key.lower(): value for key, value in values.items()}
    )


settings = load_settings()
