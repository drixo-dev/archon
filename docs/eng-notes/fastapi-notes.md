# FastAPI Notes

# What FastAPI Is

FastAPI is a modern Python backend framework for APIs.

Built on:
- ASGI
- Starlette
- Pydantic

Popular in:
- AI systems
- ML serving
- backend APIs
- internal platforms

---

# Important Distinction

FastAPI != Web Server

FastAPI:
application framework

Uvicorn:
runtime server

---

# ASGI

Asynchronous Server Gateway Interface.

Modern async alternative to WSGI.

Supports:
- async requests
- websockets
- concurrency

---

# Basic FastAPI Example

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hello"}
```

---

# Route Registration

```python
@app.get("/")
```

Maps:
HTTP request → Python function

---

# Async Functions

```python
async def
```

Important because APIs spend lots of time:
waiting.

Examples:
- DB calls
- network requests
- file IO

Async improves concurrency efficiency.

---

# Request Lifecycle

Browser
    ↓
HTTP Request
    ↓
Uvicorn
    ↓
FastAPI Router
    ↓
Endpoint Function
    ↓
Response
    ↓
Browser

---

# OpenAPI Docs

FastAPI auto-generates:
- API docs
- schemas
- Swagger UI

Available at:
/docs

Huge productivity advantage.

---

# Pydantic

Validation system.

Example:

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
```

Ensures structured valid data.

---

# Why Validation Matters

Backend systems constantly receive:
- invalid
- malformed
- malicious

data.

Validation protects system integrity.

---

# HTTP Methods

## GET

Read data.

---

## POST

Create data.

---

## PUT

Replace/update resource.

---

## DELETE

Remove resource.

---

# Status Codes

## 200

Success

---

## 404

Not found

---

## 500

Server error

---

# Uvicorn

ASGI server.

Starts FastAPI app.

Example:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

# Important Networking Note

0.0.0.0 means:
listen on all interfaces.

Critical inside containers.

---

# Common Beginner Mistakes

## Blocking code inside async

Bad:

time.sleep()

Good:

await asyncio.sleep()

---

## Using localhost inside containers incorrectly

Container localhost refers to container itself.

---

# Production Relevance

FastAPI heavily used in:
- AI infrastructure
- retrieval systems
- ML APIs
- internal backend tooling
- inference services
