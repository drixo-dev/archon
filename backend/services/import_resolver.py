from pathlib import Path

class ImportResolver:

    def build_module_index(
        self,
        repository_path: Path,
        python_files: list[Path]
    ):
        """
        Build module lookup index for repository files.

        Example:

        app/services/user_service.py
            ->
        app.services.user_service
        """

        module_index = {}

        for file_path in python_files:

            relative_path = file_path.relative_to(
                repository_path
            )

            # Convert:
            # app/services/user_service.py
            # ->
            # app.services.user_service
            module_name = str(relative_path)

            module_name = module_name.replace("/", ".")
            module_name = module_name.replace(".py", "")

            module_index[module_name] = str(relative_path)

        return module_index
    
    def resolve_import(
    self,
    module_name: str,
    module_index: dict
    ):
        """
        Resolve import module name to repository file.

        Example:

        tests.utils
            ->
        tests/utils.py
        """

        return module_index.get(module_name)

import_resolver = ImportResolver()