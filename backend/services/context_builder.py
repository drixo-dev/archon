from app.config import settings
from repositories.embedding_repository import embedding_repository
from services.embedding_service import embedding_service
from services.graph_service import graph_service

class ContextBuilder:

    def build_context(
        self,
        question: str,
        retrieval_limit: int = settings.CONTEXT_RETRIEVAL_LIMIT,
        same_file_limit: int = settings.CONTEXT_SAME_FILE_LIMIT,
        dependency_limit: int = settings.CONTEXT_DEPENDENCY_LIMIT,
        call_neighbor_limit: int = settings.CONTEXT_CALL_NEIGHBOR_LIMIT,
        max_total_functions: int = settings.CONTEXT_MAX_TOTAL_FUNCTIONS,
        repository_id: str | None = None
    ):
        query_embedding = embedding_service.generate_embedding(question)

        matches = embedding_repository.search_similar(
            query_embedding=query_embedding,
            limit=retrieval_limit,
            repository_id=repository_id
        )

        retrieved_functions = [
            self._function_from_search_result(result)
            for result in matches
        ]

        return self.expand_context(
            question=question,
            retrieved_functions=retrieved_functions,
            repository_id=repository_id,
            same_file_limit=same_file_limit
        )

    def expand_context(
        self,
        question: str,
        retrieved_functions: list[dict],
        repository_id: str | None = None,
        same_file_limit: int = settings.CONTEXT_SAME_FILE_LIMIT
    ):
        # 1. Group by source file
        candidate_files = {}
        for func in retrieved_functions:
            fp = func["file_path"]
            if fp not in candidate_files:
                candidate_files[fp] = []
            candidate_files[fp].append(func)

        # 2. Score each file
        all_stats = graph_service.get_file_statistics_for_folders(repository_id) if repository_id else []
        stats_by_file = {s["path"]: s for s in all_stats}

        scored_files = []
        for fp, funcs in candidate_files.items():
            semantic_score = len(funcs) * 10
            stats = stats_by_file.get(fp, {"incoming_deps": 0, "outgoing_deps": []})
            
            proximity_score = 0
            for dep in stats.get("outgoing_deps", []):
                if dep in candidate_files:
                    proximity_score += 5
                    
            call_frequency = stats.get("incoming_deps", 0) * 2
            
            total_score = semantic_score + proximity_score + call_frequency
            scored_files.append({
                "file_path": fp,
                "score": total_score,
                "functions": funcs,
                "dependencies": stats.get("outgoing_deps", []),
                "incoming_deps": stats.get("incoming_deps", 0)
            })

        # Sort and take top 5
        scored_files.sort(key=lambda x: x["score"], reverse=True)
        top_files = scored_files[:5]

        # 3. Expand to related files/functions using Neo4j
        feature_files = []
        for f in top_files:
            file_funcs = graph_service.get_functions_by_file(f["file_path"], limit=max(5, same_file_limit))
            seen = {fn["qualified_name"] for fn in f["functions"]}
            merged_funcs = list(f["functions"])
            for fn in file_funcs:
                if fn["qualified_name"] not in seen:
                    merged_funcs.append(fn)
                    seen.add(fn["qualified_name"])

            feature_files.append({
                "file_path": f["file_path"],
                "score": f["score"],
                "functions": merged_funcs,
                "dependencies": f["dependencies"]
            })

        total_files = len(feature_files)
        total_functions = sum(len(f["functions"]) for f in feature_files)

        return {
            "question": question,
            "feature_files": feature_files,
            "metadata": {
                "files": total_files,
                "functions": total_functions,
                "graph_expansion": "1 hops"
            }
        }

    def _function_from_search_result(self, result):
        return {
            "qualified_name": result[0],
            "file_path": result[1],
            "source_code": result[2]
        }

context_builder = ContextBuilder()
