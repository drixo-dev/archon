from fastapi import APIRouter

from models.repository import RepositoryCreateRequest, RepositoryListResponse, RepositoryResponse
from services.repository_service import repository_service

router = APIRouter()


@router.post("/repositories", response_model=RepositoryResponse)
def create_repository(request: RepositoryCreateRequest):
    return repository_service.create_repository(request.github_url)


@router.get("/repositories", response_model=RepositoryListResponse)
def list_repositories():
    return {"repositories": repository_service.list_repositories()}
