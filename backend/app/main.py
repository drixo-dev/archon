from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.chat import router as chat_router
from api.repositories import router as repositories_router
from app.db.neo4j import neo4j_connection
from app.db.postgres import postgres_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    postgres_connection.connect()
    neo4j_connection.connect()
    try:
        yield
    finally:
        neo4j_connection.close()
        postgres_connection.close()


app = FastAPI(title="Archon API", lifespan=lifespan)

app.include_router(chat_router)
app.include_router(repositories_router)


@app.get("/")
async def root():
    return {"message": "Archon API is running"}
