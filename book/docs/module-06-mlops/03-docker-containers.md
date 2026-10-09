---
id: 03-docker-containers
title: Docker Containers
sidebar_position: 3
---

# Docker Containers

## 1. Why Containers?

A machine learning application may depend on a particular Python version, operating system libraries, and package versions. **Docker** packages the application and its environment into a reproducible container image.

```text
Application + Dependencies + Runtime
                ↓
             Docker Image
                ↓
          Running Container
```

## 2. Basic Dockerfile

Example for a FastAPI ML service:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 3. Build and Run

```bash
docker build -t ml-api .
docker run -p 8000:8000 ml-api
```

The API can then be accessed through port 8000.

## 4. requirements.txt

Keep dependencies explicit:

```text
fastapi
uvicorn
scikit-learn
joblib
```

For professional projects, pin compatible versions after testing.

## 5. Important Docker Concepts

- **Image:** packaged blueprint.
- **Container:** running instance of an image.
- **Dockerfile:** instructions for building an image.
- **Port mapping:** connects a host port to a container port.
- **Volume:** persistent or shared storage.

## 6. Good Practices

- Use small base images where practical.
- Do not put passwords or API keys in the Dockerfile.
- Use `.dockerignore`.
- Keep images focused on one service.
- Test the exact image you plan to deploy.

## Exercise

Containerize your FastAPI prediction service and verify that `/health` and `/predict` work from inside the container.
