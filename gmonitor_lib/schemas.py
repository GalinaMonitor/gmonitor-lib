from enum import StrEnum, auto

from pydantic import BaseModel


class TopicsEnum(StrEnum):
    """
    Перечисление тем для обмена сообщениями.
    """
    GPT_BOT_RESULT = "gpt_bot_result"
    GPT_BOT_REQUEST = "gpt_bot_request"


class GptDtoType(StrEnum):
    """
    Перечисление типов ответов от GPT модели.
    """
    IMAGE = auto()  # Изображение
    TEXT = auto()   # Текст
    AUDIO = auto()  # Аудио


class GptDto(BaseModel):
    """
    Модель данных для передачи ответов от GPT.
    """
    content: str  # Содержимое ответа
    is_error: bool = False  # Флаг ошибки
    chat_id: int | None = None  # Идентификатор чата
    type: GptDtoType = GptDtoType.TEXT  # Тип ответа
