from enum import StrEnum, auto

from pydantic import BaseModel


class TopicsEnum(StrEnum):
    GPT_BOT_RESULT = "gpt_bot_result"
    GPT_BOT_REQUEST = "gpt_bot_request"


class GptResponseType(StrEnum):
    IMAGE = auto()
    TEXT = auto()


class GptResponse(BaseModel):
    chat_id: int
    text: str = ""
    type: GptResponseType = GptResponseType.TEXT


class GptRequest(BaseModel):
    chat_id: int
    text: str
