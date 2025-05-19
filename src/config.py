#src/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Класс для конфигурации приложения, загружающий настройки из .env файла и переменных окружения.

    Атрибуты:
       base_url (str): Базовый URL API сервиса.
       user_name (str): Имя пользователя для аутентификации.
       password (str): Пароль пользователя для аутентификации.
    """
    base_url: str
    user_name: str
    password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()