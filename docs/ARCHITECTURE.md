# Architecture

```text
Raw data -> ML pipeline -> artifact files -> FastAPI services -> React dashboard
```

## How Docker works in this project

- Backend Dockerfile installs Python dependencies first, then copies the app and artifact directory. This ordering improves layer caching.
- Frontend Dockerfile builds the Vite bundle in a Node container and serves it via Nginx.
- docker-compose wires the backend and frontend together so the frontend can reach the backend by its service name.
- Use `docker compose build`, `docker compose up`, `docker compose down`, and `docker compose logs -f backend` for local development.
