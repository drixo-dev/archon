# Docker Fundamentals

# What Problem Docker Solves

Before Docker, backend applications often failed with:

- "works on my machine"
- dependency conflicts
- different OS behavior
- difficult onboarding
- inconsistent environments

Example:

Developer A:
- Python 3.10
- Ubuntu
- PostgreSQL 15

Developer B:
- Python 3.12
- Windows
- PostgreSQL 16

Application behaves differently.

Docker solves this by packaging:
- runtime
- dependencies
- filesystem
- environment

inside isolated containers.

---

# Core Mental Model

Docker is NOT a virtual machine.

Docker containers:
- share the host kernel
- isolate processes/users/filesystems
- are lightweight

Think:

Host OS
    ↓
Docker Engine
    ↓
Containers

---

# Image vs Container

## Image

Blueprint/template.

Contains:
- OS layer
- runtime
- dependencies
- application code

Example:
python:3.12-slim

Images are:
- immutable
- layered
- reusable

---

## Container

Running instance of image.

Think:

Image = class
Container = object instance

Container characteristics:
- isolated
- ephemeral
- networked
- process-based

---

# Important Docker Architecture

## Docker CLI

Command-line tool.

Example:
docker run
docker ps

CLI only sends commands.

---

## Docker Daemon

Background service.

Responsible for:
- building images
- starting containers
- managing networks
- managing volumes

Important concept:

Docker CLI != Docker Engine

---

# Dockerfile

Defines how image is built.

Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

---

# Important Instructions

## FROM

Base image.

Starting filesystem layer.

---

## WORKDIR

Working directory inside container.

Equivalent to:
cd /app

---

## COPY

Copies files:
host → container

---

## RUN

Build-time command.

Creates new image layer.

Example:
RUN pip install ...

---

## CMD

Runtime startup command.

Executed when container starts.

---

# Docker Layers

Every Dockerfile instruction creates layer.

Benefits:
- caching
- reuse
- faster rebuilds

Important optimization:

COPY requirements.txt .
RUN pip install ...

COPY . .

Dependencies change less frequently than code.

---

# Container Networking

Containers are isolated.

localhost inside container refers to:
THE CONTAINER ITSELF

NOT host machine.

This is extremely important.

---

# Port Mapping

Example:

8000:8000

Format:
HOST:CONTAINER

Host port exposed to local machine.

---

# Volumes

Containers are ephemeral.

Deleting container removes internal filesystem changes.

Volumes provide persistence.

Important for:
- databases
- uploaded files
- durable storage

---

# Bind Mounts

Example:

./backend:/app

Synchronizes:
host folder ↔ container folder

Used heavily in development.

---

# Docker Lifecycle

## Build

docker build

Creates image.

---

## Run

docker run

Starts container.

---

## Stop

docker stop

Stops running container.

---

## Remove

docker rm

Deletes container.

---

# Important Commands

## Running Containers

docker ps

---

## All Containers

docker ps -a

---

## Logs

docker logs <container>

---

## Build

docker build .

---

## Start Compose System

docker compose up --build

---

## Stop Compose System

docker compose down

---

# Common Beginner Mistakes

## Using localhost incorrectly

Inside container:
localhost = same container

Use service names in Compose.

---

## Forgetting volume persistence

Without volumes:
database data disappears.

---

## Forgetting rebuild

Changing requirements.txt usually requires:
docker compose up --build

---

# Production Relevance

Docker is heavily used in:
- backend systems
- AI infrastructure
- microservices
- cloud deployment
- CI/CD pipelines
- Kubernetes

Docker became foundational infrastructure tooling.
