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
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


class ExternalHttpRequestError(Exception):
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
    def __init__(
        self,
        verify: bool = True,
    ):
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
        Отправка запроса через httpx

        Args:
            url: Полный url
            method: Метод запроса
            data: Данные для post/put/patch запросов
            parser: Парсер для обработки ответа httpx
            **kwargs: Аргументы, передаваемые в httpx.request()
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
    def __init__(self):
        self.session = boto3.client(
            "s3",
            endpoint_url=settings.aws_host,
            region_name="ru-1",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            config=Config(s3={"addressing_style": "path"}),
        )
        self.bucket_name = settings.aws_bucket_name

    def upload_file(self, file_io: io.BytesIO, filename: str) -> None:
        self.session.upload_fileobj(file_io, Bucket=self.bucket_name, Key=filename)

    def download_file(self, filename: str) -> io.BytesIO:
        file_io = io.BytesIO()
        self.session.download_fileobj(self.bucket_name, filename, file_io)
        file_io.seek(0)
        return file_io

    def delete_file(self, filename: str) -> None:
        self.session.delete_object(Bucket=self.bucket_name, Key=filename)