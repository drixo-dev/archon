from pathlib import Path

from parser.python_parser import extract_file_structure
from services.graph_service import graph_service
from services.import_resolver import import_resolver


class GraphBuilder:

    def ingest_file(
        self,
        repository_name: str,
        repository_path: Path,
        file_path: Path,
        module_index: dict = None
    ):

        structure = extract_file_structure(file_path)

        relative_path = str(
            file_path.relative_to(repository_path)
        )

        # Create File Node
        graph_service.create_file(
            repository_name=repository_name,
            file_path=relative_path
        )

        # Create Function Nodes
        for function_name in structure["functions"]:

            graph_service.create_function(
                file_path=relative_path,
                function_name=function_name
            )

        # Create Import Nodes + Relationships
        for import_data in structure["imports"]:

            # Skip invalid imports
            if not import_data.get("module"):
                continue

            graph_service.create_import_node(
                module=import_data["module"],
                import_type=import_data["type"],
                alias=import_data.get("alias"),
                imported_name=import_data.get("name")
            )

            graph_service.create_file_import_relationship(
                file_path=relative_path,
                module=import_data["module"],
                import_type=import_data["type"],
                alias=import_data.get("alias"),
                imported_name=import_data.get("name")
            )

            # Resolve internal repository dependencies
            if module_index:

                resolved_path = import_resolver.resolve_import(
                    module_name=import_data["module"],
                    module_index=module_index
                )

                # Only create dependency relationship
                # for internal repository imports
                if resolved_path:

                    graph_service.create_dependency_relationship(
                        source_file_path=relative_path,
                        target_file_path=resolved_path
                    )


graph_builder = GraphBuilder()