from ingestion.github_loader import clone_repository
from ingestion.scanner import scan_python_files
from parser.python_parser import extract_file_structure
from pprint import pprint

REPO_URL = "https://github.com/fastapi/fastapi.git"


repo_path = clone_repository(REPO_URL)

python_files = scan_python_files(repo_path)

print(f"Found {len(python_files)} Python files")


first_file = python_files[0]

print(f"\nParsing file: {first_file}")

structure = extract_file_structure(first_file)

print("\nExtracted Structure:\n")

pprint(structure)