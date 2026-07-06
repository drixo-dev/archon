from repositories.embedding_repository import (
    embedding_repository
)
from services.embedding_service import (
    embedding_service
)
from services.graph_service import (
    graph_service
)


class ContextBuilder:

    def build_context(
        self,
        question: str,
        retrieval_limit: int = 3,
        same_file_limit: int = 8,
        dependency_limit: int = 8
    ):
        query_embedding = (
            embedding_service.generate_embedding(
                question
            )
        )

        matches = (
            embedding_repository.search_similar(
                query_embedding=query_embedding,
                limit=retrieval_limit
            )
        )

        retrieved_functions = [
            self._function_from_search_result(result)
            for result in matches
        ]

        return self.expand_context(
            question=question,
            retrieved_functions=retrieved_functions,
            same_file_limit=same_file_limit,
            dependency_limit=dependency_limit
        )

    def expand_context(
        self,
        question: str,
        retrieved_functions: list[dict],
        same_file_limit: int = 8,
        dependency_limit: int = 8
    ):
        seen = set()

        context = {
            "question": question,
            "retrieved_functions": [],
            "same_file_functions": [],
            "call_neighbor_functions": [],
            "dependency_functions": []
        }

        for function in retrieved_functions:
            self._append_unique(
                items=context["retrieved_functions"],
                function=function,
                seen=seen
            )

            same_file_functions = (
                graph_service.get_functions_by_file(
                    file_path=function["file_path"],
                    limit=same_file_limit
                )
            )

            for same_file_function in same_file_functions:
                self._append_unique(
                    items=context["same_file_functions"],
                    function=same_file_function,
                    seen=seen
                )

            neighbors = (
                graph_service.get_function_neighbors(
                    function["qualified_name"]
                )
            )

            if neighbors:
                neighbor_names = (
                    neighbors["callers"]
                    + neighbors["callees"]
                )

                neighbor_functions = (
                    graph_service
                    .get_functions_by_qualified_names(
                        neighbor_names
                    )
                )

                for neighbor_function in neighbor_functions:
                    self._append_unique(
                        items=context[
                            "call_neighbor_functions"
                        ],
                        function=neighbor_function,
                        seen=seen
                    )

            dependency_functions = (
                graph_service.get_dependency_functions(
                    file_path=function["file_path"],
                    limit=dependency_limit
                )
            )

            for dependency_function in dependency_functions:
                self._append_unique(
                    items=context["dependency_functions"],
                    function=dependency_function,
                    seen=seen
                )

        return context

    def _function_from_search_result(
        self,
        result
    ):
        return {
            "qualified_name": result[0],
            "file_path": result[1],
            "source_code": result[2]
        }

    def _append_unique(
        self,
        items: list,
        function: dict,
        seen: set
    ):
        qualified_name = function["qualified_name"]

        if qualified_name in seen:
            return

        seen.add(qualified_name)
        items.append(function)


context_builder = ContextBuilder()
