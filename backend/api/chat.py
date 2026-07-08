from fastapi import APIRouter

from models.chat import ChatRequest, ChatResponse
from services.chat_service import chat_service


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    result = chat_service.chat(
        repository=request.repository_id,
        question=request.question
    )

    return ChatResponse(**result)
