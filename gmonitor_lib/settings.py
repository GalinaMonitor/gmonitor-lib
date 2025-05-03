import logging

from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.WARNING)


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    Содержит параметры для подключения к AWS S3.
    """
    aws_host: str = "host"  # Хост AWS S3
    aws_bucket_name: str = "bucket"  # Имя бакета
    aws_access_key_id: str = "access_key_id"  # Идентификатор ключа доступа
    aws_secret_access_key: str = "secret_access_key"  # Секретный ключ доступа

settings = Settings()
