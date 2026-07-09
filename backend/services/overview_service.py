from app.config import settings
import json

from services.context_builder import context_builder
from services.llm_service import llm_service
from services.prompt_builder import prompt_builder
from services.repository_service import repository_service


class OverviewService:

    def generate_overview(self, repository_id: str) -> dict:
        repository = repository_service.get_repository(repository_id)
        if not repository:
            return None

        question = prompt_builder.OVERVIEW_QUESTION
        
        context = context_builder.build_context(
            question=question,
            repository_id=repository_id,
            retrieval_limit=settings.OVERVIEW_RETRIEVAL_LIMIT,
            same_file_limit=settings.OVERVIEW_SAME_FILE_LIMIT,
            dependency_limit=settings.OVERVIEW_DEPENDENCY_LIMIT,
            call_neighbor_limit=settings.OVERVIEW_CALL_NEIGHBOR_LIMIT,
            max_total_functions=settings.OVERVIEW_MAX_TOTAL_FUNCTIONS
        )

        prompt = prompt_builder.build_repository_overview_prompt(
            repository_name=repository.get("name", repository_id) if isinstance(repository, dict) else getattr(repository, "name", repository_id),
            repository_context=context
        )

        try:
            answer = llm_service.generate_answer(prompt)
            return llm_service.extract_json(answer)
        except json.JSONDecodeError:
            return {"error": "Failed to parse overview JSON", "raw_response": answer}
        except Exception as error:
            return {"error": f"Failed to generate overview: {error}"}


overview_service = OverviewService()
