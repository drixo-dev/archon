import ast
from pathlib import Path


def parse_python_file(file_path: Path):
    """
    Parse Python file into AST.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.read()

    tree = ast.parse(source_code)

    return tree


def extract_imports(tree):
    """
    Extract import statements from AST.
    """

    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


def extract_functions(tree):
    """
    Extract function definitions.
    """

    functions = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

    return functions

def extract_function_calls(tree):
    """
    Extract function calls from AST.
    """

    calls = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)

            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)

    return calls

def extract_file_structure(file_path: Path):
    """
    Extract complete semantic structure from Python file.
    """

    tree = parse_python_file(file_path)

    return {
        "file": str(file_path),
        "imports": extract_imports(tree),
        "functions": extract_functions(tree),
        "calls": extract_function_calls(tree),
    }