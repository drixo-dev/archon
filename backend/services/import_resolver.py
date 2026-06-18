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

    def build_function_index(
        self,
        repository_path: Path,
        python_files: list[Path]
    ):
        """
        Build function lookup index.

        Example:

        validate_user
            ->
        auth/utils.py:validate_user
        """

        from parser.python_parser import (
            extract_file_structure
        )

        function_index = {}

        for file_path in python_files:

            relative_path = str(
                file_path.relative_to(repository_path)
            )

            structure = extract_file_structure(
                file_path
            )

            for function_data in structure["functions"]:

                function_name = function_data["name"]

                qualified_name = (
                    f"{relative_path}:{function_name}"
                )

                function_index[
                    function_name
                ] = qualified_name

        return function_index

    def resolve_function(
        self,
        function_name: str,
        function_index: dict
    ):
        """
        Resolve function name to
        qualified function identifier.
        """

        return function_index.get(function_name)

import_resolver = ImportResolver()