from ingestion.github_loader import clone_repository
from ingestion.scanner import scan_python_files
from parser.python_parser import (
    parse_python_file,
    extract_imports,
    extract_functions,
    extract_function_calls,
)


REPO_URL = "https://github.com/fastapi/fastapi.git"


repo_path = clone_repository(REPO_URL)

python_files = scan_python_files(repo_path)

print(f"Found {len(python_files)} Python files")


first_file = python_files[0]

print(f"\nParsing file: {first_file}")


tree = parse_python_file(first_file)

imports = extract_imports(tree)

calls = extract_function_calls(tree)

functions = extract_functions(tree)


print("\nImports:")
print(imports[:10])

print("\nFunctions:")
print(functions[:10])

print("\nFunction Calls:")
print(calls[:20])