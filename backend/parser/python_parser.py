import ast
from pathlib import Path


def parse_python_file(file_path: Path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        source_code = file.read()

    tree = ast.parse(source_code)

    return tree, source_code


def extract_imports(tree):
    """
    Extract structured import information from AST.
    """

    imports = []

    for node in ast.walk(tree):

        # import os
        # import numpy as np
        if isinstance(node, ast.Import):

            for alias in node.names:
                imports.append({
                    "module": alias.name,
                    "type": "import",
                    "alias": alias.asname
                })

        # from services.user_service import create_user
        elif isinstance(node, ast.ImportFrom):

            module_name = node.module

            for alias in node.names:
                imports.append({
                    "module": module_name,
                    "type": "from_import",
                    "name": alias.name,
                    "alias": alias.asname
                })

    return imports


def extract_functions(tree, source_code):
    """
    Extract functions with source code.
    """

    functions = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            function_source = ast.get_source_segment(
                source_code,
                node
            )

            functions.append({
                "name": node.name,
                "source": function_source
            })

    return functions


def extract_function_calls(tree):
    """
    Extract caller -> callee relationships.
    """

    calls = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            caller = node.name

            for child in ast.walk(node):

                if isinstance(child, ast.Call):

                    callee = None

                    if isinstance(child.func, ast.Name):
                        callee = child.func.id

                    elif isinstance(child.func, ast.Attribute):
                        callee = child.func.attr

                    if callee:

                        calls.append({
                            "caller": caller,
                            "callee": callee
                        })

    return calls


def extract_file_structure(file_path: Path):
    """
    Extract complete semantic structure from Python file.
    """

    tree, source_code = parse_python_file(
    file_path
    )

    return {
        "file": str(file_path),
        "imports": extract_imports(tree),
        "functions": extract_functions(tree,source_code),
        "calls": extract_function_calls(tree),
    }