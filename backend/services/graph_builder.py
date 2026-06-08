from pathlib import Path
from parser.python_parser import extract_file_structure
from services.graph_service import graph_service

class GraphBuilder:

    def ingest_file(
        self,
        repository_name: str,
        repository_path: Path,
        file_path: Path
    ):
        structure = extract_file_structure(file_path)

        relative_path = str(
            file_path.relative_to(repository_path)
        )

        graph_service.create_file(
            repository_name=repository_name,
            file_path=relative_path
        )

        for function_name in structure["functions"]:
            graph_service.create_function(
                file_path=relative_path,
                function_name=function_name
            )


graph_builder = GraphBuilder()
