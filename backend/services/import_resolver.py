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
        Build function lookup index mapping bare names to lists of qualified names.
        """
        from parser.python_parser import extract_file_structure

        function_index = {}

        for file_path in python_files:
            relative_path = str(file_path.relative_to(repository_path))
            structure = extract_file_structure(file_path)

            for function_data in structure["functions"]:
                function_name = function_data["name"]
                bare_name = function_name.split('.')[-1]
                qualified_name = f"{relative_path}:{function_name}"

                if bare_name not in function_index:
                    function_index[bare_name] = []
                function_index[bare_name].append(qualified_name)
                
                if function_name != bare_name:
                    if function_name not in function_index:
                        function_index[function_name] = []
                    function_index[function_name].append(qualified_name)

        return function_index

    def resolve_function(
        self,
        function_name: str,
        function_index: dict,
        current_file: str = None,
        imports: list = None,
        module_index: dict = None
    ):
        """
        Resolve function name to qualified function identifier
        using current file and import context.
        """
        candidates = function_index.get(function_name, [])
        if not candidates:
            return None
            
        if len(candidates) == 1:
            return candidates[0]
            
        if current_file:
            for cand in candidates:
                if cand.startswith(current_file + ":"):
                    return cand
                    
        if imports and module_index:
            for imp in imports:
                if imp.get("type") == "from_import" and imp.get("name") == function_name:
                    mod_path = module_index.get(imp.get("module"))
                    if mod_path:
                        for cand in candidates:
                            if cand.startswith(mod_path + ":"):
                                return cand
                elif imp.get("type") == "import":
                    mod_path = module_index.get(imp.get("module"))
                    if mod_path:
                        for cand in candidates:
                            if cand.startswith(mod_path + ":"):
                                return cand

        return candidates[0]

import_resolver = ImportResolver()