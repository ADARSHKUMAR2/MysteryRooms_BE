# Cloud Run Deployment Guide with Secret Manager

Complete guide for deploying multi-service FastAPI applications to Google Cloud Run using Docker, Artifact Registry, and Secret Manager.

## Quick Start

### Prerequisites
```bash
gcloud --version
docker --version
python --version
```

### Setup GCP
```bash
export GCP_PROJECT="your-project-id"
export GCP_REGION="asia-south1"
gcloud config set project ${GCP_PROJECT}
gcloud services enable run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
```

## Architecture

**Single Image, Multiple Services:**
- One Docker image tagged as: auth, game, gateway
- Different startup commands per service
- Secrets mounted from Google Secret Manager

## Key Concepts

### 1. Load Environment Variables FIRST

**CRITICAL:** Load dotenv before importing local modules:

```python
from dotenv import load_dotenv, find_dotenv
import os

# Load FIRST
load_dotenv(os.getenv("DOTENV_PATH", find_dotenv()))

# Then import local modules
from backend.services.auth.config.db import init_auth_db
```

### 2. Dockerfile with Symlink

```dockerfile
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .

# CRITICAL: Symlink for backend.* imports
RUN ln -s /app /app/backend

ENV PYTHONPATH=/app
EXPOSE 8000 8001 8002
CMD ["uv", "run", "uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Secret Management

```bash
# Upload .env-prod
gcloud secrets create py-env-file \
  --project=${GCP_PROJECT} \
  --replication-policy=automatic \
  --data-file=.env-prod

# Grant access
export SA=$(gcloud iam service-accounts list \
  --project=${GCP_PROJECT} \
  --filter="email:compute@developer.gserviceaccount.com" \
  --format="value(email)")

gcloud secrets add-iam-policy-binding py-env-file \
  --project=${GCP_PROJECT} \
  --member="serviceAccount:${SA}" \
  --role="roles/secretmanager.secretAccessor"
```

## Build and Deploy

### 1. Build Image

```bash
cd backend
docker build \
  --platform linux/amd64 \
  -t ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/mysteryrooms-repo/backend:latest \
  .
```

### 2. Tag and Push

```bash
docker tag \
  ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/mysteryrooms-repo/backend:latest \
  ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/mysteryrooms-repo/backend:auth

docker push ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/mysteryrooms-repo/backend:auth
```

### 3. Deploy to Cloud Run

```bash
gcloud run deploy mysteryrooms-auth \
  --project=${GCP_PROJECT} \
  --region=${GCP_REGION} \
  --image=${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/mysteryrooms-repo/backend:auth \
  --command=uv \
  --args=run,uvicorn,services.auth.main:app,--host,0.0.0.0,--port,8001 \
  --port=8001 \
  --memory=1Gi \
  --set-env-vars=DOTENV_PATH=/secrets/py_env_file \
  --set-secrets=/secrets/py_env_file=py-env-file:latest
```

## Common Issues

### ModuleNotFoundError: No module named 'backend'
**Fix:** Add symlink in Dockerfile: `RUN ln -s /app /app/backend`

### Environment variables undefined
**Fix:** Load dotenv BEFORE local imports

### Permission denied on secret
**Fix:** Grant IAM permissions to service account

### Container failed to start
**Fix:** Read logs to find actual error

## Security Checklist

- [ ] Secrets in .gitignore
- [ ] No secrets in Docker images
- [ ] Service accounts use least privilege
- [ ] Rotate exposed credentials immediately

## Deployment Checklist

- [ ] Update .env-prod
- [ ] Upload to Secret Manager
- [ ] Build Docker image
- [ ] Push with correct tags
- [ ] Deploy services
- [ ] Test health endpoints

---

**Last Updated:** 2026-09-07 | **Version:** 1.0
