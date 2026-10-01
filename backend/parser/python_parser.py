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


class StructureVisitor(ast.NodeVisitor):
    def __init__(self, source_code):
        self.source_code = source_code
        self.scope_stack = []
        self.functions = []
        self.calls = []

    def visit_FunctionDef(self, node):
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node):
        self._visit_func(node)

    def _visit_func(self, node):
        name = node.name
        qualified_name = ".".join(self.scope_stack + [name])
        
        function_source = ast.get_source_segment(self.source_code, node) if self.source_code else ""
        
        self.functions.append({
            "name": qualified_name,
            "source": function_source
        })
        
        self.scope_stack.append(name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_ClassDef(self, node):
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Call(self, node):
        caller = ".".join(self.scope_stack) if self.scope_stack else "<module>"
        callee = None
        
        if isinstance(node.func, ast.Name):
            callee = node.func.id
        elif isinstance(node.func, ast.Attribute):
            callee = node.func.attr
            
        if callee:
            self.calls.append({
                "caller": caller,
                "callee": callee
            })
            
        self.generic_visit(node)


def extract_functions(tree, source_code):
    visitor = StructureVisitor(source_code)
    visitor.visit(tree)
    return visitor.functions


def extract_function_calls(tree):
    visitor = StructureVisitor("")
    visitor.visit(tree)
    return visitor.calls


def extract_file_structure(file_path: Path):
    """
    Extract complete semantic structure from Python file.
    """

    tree, source_code = parse_python_file(file_path)
    
    visitor = StructureVisitor(source_code)
    visitor.visit(tree)

    return {
        "file": str(file_path),
        "imports": extract_imports(tree),
        "functions": visitor.functions,
        "calls": visitor.calls,
    }