from fastapi import APIRouter, HTTPException

from models.repository import (
    RepositoryCreateRequest,
    RepositoryDetailResponse,
    RepositoryListResponse,
    RepositoryResponse,
)
from services.repository_service import repository_service

router = APIRouter()


@router.post("/repositories", response_model=RepositoryResponse)
def create_repository(request: RepositoryCreateRequest):
    return repository_service.create_repository(request.github_url)


@router.get("/repositories", response_model=RepositoryListResponse)
def list_repositories():
    return {"repositories": repository_service.list_repositories()}


@router.get("/repositories/{repository_id}", response_model=RepositoryDetailResponse)
def get_repository(repository_id: str):
    repository = repository_service.get_repository(repository_id)
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    return {"repository": repository}
