# Docker Compose Notes

# What Docker Compose Solves

Docker manages single containers.

Real backend systems require:
- API service
- databases
- cache
- workers

Compose orchestrates multiple containers together.

---

# Compose Mental Model

Compose is:
Infrastructure as Code

You declaratively define:
- services
- networks
- volumes
- ports
- environment variables

inside YAML.

---

# Basic Compose Structure

```yaml
services:
  api:
    build:
      context: ./backend

  postgres:
    image: postgres:16
```

---

# Services

Each service becomes:
- container
- hostname
- network participant

Example:
api
postgres
neo4j

---

# Build Context

```yaml
build:
  context: ./backend
```

Docker only sees files inside build context.

Important for:
- security
- reproducibility
- performance

---

# Internal Networking

Compose automatically creates:
private network

All services can communicate using service names.

Example:

api connects to:
postgres

NOT localhost.

---

# Service Discovery

Compose provides automatic DNS resolution.

Example:
postgres becomes hostname.

Very important distributed systems concept.

---

# Volumes

Compose supports persistent volumes.

Example:

```yaml
volumes:
  postgres_data:
```

Used for:
- database persistence
- durable storage

---

# Bind Mounts

Example:

```yaml
volumes:
  - ./backend:/app
```

Live sync between:
host ↔ container

Useful for development.

---

# Restart Policies

Example:

restart: unless-stopped

Container auto-restarts after crash/reboot.

Important reliability concept.

---

# Environment Variables

```yaml
environment:
  POSTGRES_USER: archon
```

Used for:
- credentials
- configs
- runtime settings

Industry standard practice.

---

# Compose Lifecycle

## Start System

docker compose up

---

## Build + Start

docker compose up --build

---

## Background Mode

docker compose up -d

---

## Stop

docker compose down

---

## Logs

docker compose logs

---

## Logs Follow

docker compose logs -f

---

# Common Errors

## Port Already Allocated

Another process using same port.

---

## Container Crash Loop

Startup command failing repeatedly.

---

## Service Unreachable

Usually:
- wrong hostname
- wrong port
- container not started

---

# Production Relevance

Compose is mainly:
- local development
- integration testing
- small deployments

Large systems evolve into:
- Kubernetes
- ECS
- Nomad

But concepts remain similar:
- services
- networking
- orchestration
- scaling
