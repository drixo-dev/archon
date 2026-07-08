from pydantic import BaseModel


class ChatRequest(BaseModel):
    repository_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    context: dict
