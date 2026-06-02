from pathlib import Path

from git import Repo


REPOSITORIES_DIR = Path("/app/datasets/repositories")


def clone_repository(repo_url: str) -> Path:
    """
    Clone repository into local datasets directory.
    """

    repo_name = repo_url.split("/")[-1].replace(".git", "")

    local_path = REPOSITORIES_DIR / repo_name

    if local_path.exists():
        print(f"Repository already exists: {local_path}")
        return local_path

    print(f"Cloning repository: {repo_url}")

    Repo.clone_from(repo_url, local_path)

    print(f"Repository cloned to: {local_path}")

    return local_path