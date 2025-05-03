import io
import logging
from enum import StrEnum
from json import JSONDecodeError
from typing import Any, Callable

import boto3
from botocore.client import Config
from httpx import AsyncClient, AsyncHTTPTransport, HTTPError, Response, Auth, Request

from .settings import settings

logger = logging.getLogger(__name__)


class HttpMethod(StrEnum):
    """
    Перечисление HTTP методов, используемых для выполнения запросов.
    """
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


class ExternalHttpRequestError(Exception):
    """
    Исключение, возникающее при ошибках во время выполнения HTTP запросов к внешним сервисам.
    """
    pass


def convert_httpx_response_to_json(response: Response) -> Any:
    if response.is_error:
        try:
            error_message = response.json()
        except JSONDecodeError:
            error_message = response.text
        raise ExternalHttpRequestError(error_message)
    try:
        return response.json()
    except JSONDecodeError as e:
        logger.error(f"Response body {response.content.decode('utf-8')}")
        raise ExternalHttpRequestError(response.content.decode("utf-8")) from e


class BaseHttpxClient:
    """
    Базовый класс для HTTP клиентов, использующих библиотеку httpx.
    Предоставляет функциональность для отправки HTTP запросов.
    """
    def __init__(
        self,
        verify: bool = True,
    ):
        """
        Инициализация HTTP клиента.

        Args:
            verify: Флаг проверки SSL сертификатов при выполнении запросов.
        """
        self._verify = verify
        self._base_url = ""
        self._auth: Auth | None = None

    async def _send_request(
        self,
        path: str,
        method: HttpMethod,
        json: dict[Any, Any] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int = 5,
        parser: Callable[[Response], Any] = convert_httpx_response_to_json,
        retries: int = 0,
        **kwargs: Any,
    ) -> Any:
        """
        Отправка HTTP запроса с использованием библиотеки httpx.

        Args:
            path: Путь к ресурсу, который будет добавлен к базовому URL.
            method: HTTP метод запроса (GET, POST, PUT, PATCH, DELETE).
            json: Данные в формате JSON для отправки в теле запроса.
            params: Параметры запроса, которые будут добавлены к URL.
            timeout: Таймаут запроса в секундах.
            parser: Функция для обработки ответа от сервера.
            retries: Количество повторных попыток при неудачном запросе.
            **kwargs: Дополнительные аргументы, передаваемые в httpx.request().

        Returns:
            Результат обработки ответа функцией parser или объект Response, если parser=None.

        Raises:
            ExternalHttpRequestError: При возникновении ошибок во время выполнения запроса.
        """
        transport = AsyncHTTPTransport(retries=retries, verify=self._verify)
        async with AsyncClient(
            base_url=self._base_url,
            transport=transport,
            timeout=timeout,
            auth=self._auth,
        ) as client:
            try:
                response = await client.request(
                    method=method, url=path, json=json, params=params, **kwargs
                )
            except HTTPError as e:
                raise ExternalHttpRequestError(str(e))
        if parser is not None:
            return parser(response)
        return response


class AWSClient:
    """
    Клиент для работы с AWS S3 хранилищем.
    Предоставляет методы для загрузки, скачивания и удаления файлов.
    """
    def __init__(self):
        """
        Инициализация клиента AWS S3.
        Создает сессию с использованием настроек из конфигурации.
        """
        self.session = boto3.client(
            "s3",
            endpoint_url=settings.aws_host,
            region_name="ru-1",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            config=Config(
                s3={"addressing_style": "path"},
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required",
            ),
        )
        self.bucket_name = settings.aws_bucket_name

    def get_link(self, filename: str) -> str:
        """
        Получение публичной ссылки на файл в хранилище.

        Args:
            filename: Имя файла в хранилище.

        Returns:
            Публичная ссылка на файл.
        """
        return f"{settings.aws_host}/{self.bucket_name}/{filename}"

    def upload_file(self, file_io: io.BytesIO, filename: str) -> str:
        """
        Загрузка файла в хранилище S3.

        Args:
            file_io: Объект BytesIO с содержимым файла.
            filename: Имя файла для сохранения в хранилище.

        Returns:
            Публичная ссылка на загруженный файл.
        """
        self.session.upload_fileobj(file_io, Bucket=self.bucket_name, Key=filename)
        return self.get_link(filename)

    def download_file(self, filename: str) -> io.BytesIO:
        """
        Скачивание файла из хранилища S3.

        Args:
            filename: Имя файла в хранилище.

        Returns:
            Объект BytesIO с содержимым файла.
        """
        file_io = io.BytesIO()
        self.session.download_fileobj(self.bucket_name, filename, file_io)
        file_io.seek(0)
        return file_io

    def delete_file(self, filename: str) -> None:
        """
        Удаление файла из хранилища S3.

        Args:
            filename: Имя файла в хранилище.
        """
        self.session.delete_object(Bucket=self.bucket_name, Key=filename)
