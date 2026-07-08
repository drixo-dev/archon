from pydantic import BaseModel


class RepositoryCreateRequest(BaseModel):
    github_url: str


class RepositoryResponse(BaseModel):
    id: str
    name: str
    github_url: str
    status: str
    progress: int
    created_at: str
    files_scanned: int
    functions_indexed: int
    embeddings_generated: int
    error: str | None = None


class RepositoryListResponse(BaseModel):
    repositories: list[RepositoryResponse]


class RepositoryDetailResponse(BaseModel):
    repository: RepositoryResponse
