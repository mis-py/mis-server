from pydantic_settings import BaseSettings, SettingsConfigDict
from const import ENV_FILE


class SchedulerSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )