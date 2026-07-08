from pydantic import BaseModel


class RepositoryCreateRequest(BaseModel):
    github_url: str


class RepositoryResponse(BaseModel):
    id: str
    name: str
    github_url: str
    status: str


class RepositoryListResponse(BaseModel):
    repositories: list[RepositoryResponse]
