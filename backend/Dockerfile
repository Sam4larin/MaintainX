# Base image: Python runtime for the backend service
FROM python:3.11-slim

# Set the working directory so all commands run inside the backend app folder
WORKDIR /app

# Copy dependency list first so Docker can cache installs when code changes
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code and the trained artifacts into the image
COPY backend /app/backend
COPY ml/artifacts /app/ml/artifacts

# Expose the FastAPI port for local access
EXPOSE 8000

# Start the API with uvicorn
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
