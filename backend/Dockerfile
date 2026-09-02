# Base image: Python runtime for the backend service
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./backend-requirements.txt
COPY ml/requirements.txt ./ml-requirements.txt
RUN python -c "lines = open('ml-requirements.txt').read().splitlines(); filtered = [l for l in lines if l.strip() not in ('torch', 'pytest')]; open('ml-requirements-runtime.txt', 'w').write(chr(10).join(filtered) + chr(10))"
RUN pip install --no-cache-dir -r backend-requirements.txt -r ml-requirements-runtime.txt
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY backend /app/backend
COPY ml /app/ml
COPY data/raw /app/data/raw

RUN python -m ml.pipeline.train_all

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
