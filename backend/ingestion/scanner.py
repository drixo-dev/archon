from pathlib import Path

def scan_python_files(repository_path: Path) -> list[Path]:
    """
    Scan repository and return Python files.
    """
    python_files = []
    for path in repository_path.rglob("*.py"):
        python_files.append(path)
    return python_files