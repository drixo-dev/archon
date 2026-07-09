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

        question = "Explain the architecture, main components, and purpose of this repository."
        
        context = context_builder.build_context(
            question=question,
            repository_id=repository_id,
            retrieval_limit=10,
            same_file_limit=2,
            dependency_limit=2,
            call_neighbor_limit=2,
            max_total_functions=20
        )

        prompt = prompt_builder.build_repository_overview_prompt(
            repository_name=repository.get("name", repository_id) if isinstance(repository, dict) else getattr(repository, "name", repository_id),
            repository_context=context
        )

        try:
            answer = llm_service.generate_answer(prompt)
            clean_answer = answer.strip()
            if clean_answer.startswith("```json"):
                clean_answer = clean_answer[7:]
            if clean_answer.endswith("```"):
                clean_answer = clean_answer[:-3]
            
            clean_answer = clean_answer.strip()
            return json.loads(clean_answer)
        except json.JSONDecodeError:
            return {"error": "Failed to parse overview JSON", "raw_response": answer}
        except Exception as error:
            return {"error": f"Failed to generate overview: {error}"}


overview_service = OverviewService()
