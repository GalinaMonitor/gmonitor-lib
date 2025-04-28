import logging

from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.WARNING)


class Settings(BaseSettings):
    aws_host: str = "host"
    aws_bucket_name: str = "bucket"
    aws_access_key_id: str = "access_key_id"
    aws_secret_access_key: str = "secret_access_key"

settings = Settings()
