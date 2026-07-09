from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str


    # Limits and config constants
    SOURCE_TRUNCATION_MAX_LINES: int = 30
    SOURCE_TRUNCATION_MAX_CHARACTERS: int = 1500
    
    OVERVIEW_RETRIEVAL_LIMIT: int = 10
    OVERVIEW_SAME_FILE_LIMIT: int = 2
    OVERVIEW_DEPENDENCY_LIMIT: int = 2
    OVERVIEW_CALL_NEIGHBOR_LIMIT: int = 2
    OVERVIEW_MAX_TOTAL_FUNCTIONS: int = 20
    
    CONTEXT_RETRIEVAL_LIMIT: int = 30
    CONTEXT_SAME_FILE_LIMIT: int = 3
    CONTEXT_DEPENDENCY_LIMIT: int = 3
    CONTEXT_CALL_NEIGHBOR_LIMIT: int = 4
    CONTEXT_MAX_TOTAL_FUNCTIONS: int = 12

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
