from services.context_builder import context_builder
from services.llm_service import LLMService
from services.prompt_builder import prompt_builder


class ChatService:
    def __init__(self):
        self.llm_service = LLMService()

    def chat(
        self,
        repository: str,
        question: str
    ) -> dict:
        repository_context = context_builder.build_context(
            question=question,
            repository_id=repository
        )
        prompt = prompt_builder.build_repository_chat_prompt(
            question=question,
            repository_context=repository_context,
            repository_name=repository
        )
        try:
            answer = self.llm_service.generate_answer(prompt)
        except Exception as error:
            answer = (
                "I could not generate a full answer because the language model is currently unavailable. "
                f"Details: {error}"
            )

        return {
            "answer": answer,
            "context": repository_context
        }


chat_service = ChatService()
