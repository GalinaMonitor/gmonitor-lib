# GMonitor Library

Библиотека с общим функционалом для работы с HTTP-запросами и AWS S3.

## Установка

```bash
pip install git+https://github.com/GalinaMonitor/gmonitor-lib.git
```

## Требования

- Python 3.13+
- Зависимости:
  - pydantic==2.11.3
  - httpx==0.28.1
  - boto3==1.38.4
  - pydantic_settings==2.9.1

## Функциональность

### HTTP-клиент

Библиотека предоставляет базовый HTTP-клиент на основе httpx для выполнения асинхронных HTTP-запросов:

```python
from gmonitor_lib.clients import BaseHttpxClient, HttpMethod

# Создание экземпляра клиента
client = BaseHttpxClient(verify=True)
client._base_url = "https://api.example.com"

# Выполнение запроса
response = await client._send_request(
    path="/endpoint",
    method=HttpMethod.GET,
    params={"param1": "value1"},
    timeout=10,
    retries=3
)
```

### AWS S3 клиент

Библиотека предоставляет клиент для работы с AWS S3:

```python
from gmonitor_lib.clients import AWSClient
import io

# Создание экземпляра клиента
aws_client = AWSClient()

# Загрузка файла
file_data = io.BytesIO(b"file content")
file_url = aws_client.upload_file(file_data, "filename.txt")

# Скачивание файла
downloaded_file = aws_client.download_file("filename.txt")

# Удаление файла
aws_client.delete_file("filename.txt")

# Получение ссылки на файл
file_link = aws_client.get_link("filename.txt")
```

### Схемы данных

Библиотека содержит схемы данных для работы с функционалом [GptAll](https://github.com/GalinaMonitor/gmonitor-all):

## Настройка

Библиотека использует pydantic_settings для конфигурации.Настройки для s3 можно задать через переменные окружения:

- AWS_HOST
- AWS_BUCKET_NAME
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
