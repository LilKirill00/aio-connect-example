from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Вместо str использовать SecretStr для конфиденциальных данных
    API_LOGIN: SecretStr
    API_PASSWORD: SecretStr

    SERVER_API: str

    BASE_WEBHOOK_URL: str
    WEBHOOK_PATH: str

    WEB_SERVER_HOST: str
    WEB_SERVER_PORT: int

    LINE_ID: str

    # other data
    SERVICE_REQUEST_CHANNEL_ID: str
    SERVICE_KIND_ID: str
    SERVICE_REQUEST_TYPE_ID: str
    EXECUTOR_ID: str

    # Настройки класса настроек задаются через model_config
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
