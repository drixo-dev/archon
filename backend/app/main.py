from fastapi import FastAPI

app = FastAPI(title="Archon API")


@app.get("/")
async def root():
    return {"message": "Archon API is running"}