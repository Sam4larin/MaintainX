# Base image: Python runtime for the backend service
FROM python:3.11-slim

WORKDIR /app

# Copy dependency list first so Docker can cache installs when code changes
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy backend code, ml source (model classes are imported at runtime), and
# the real raw datasets used to train inside the image -- ml/artifacts/ is
# correctly gitignored (it's generated output, not source), so it does not
# exist on a fresh clone/build context. It must be generated here, not
# copied from a path that only exists after someone has run the pipeline
# locally. The real datasets (not the smaller CI sample) are used here.
COPY backend /app/backend
COPY ml /app/ml
COPY data/raw /app/data/raw

# Train inside the image using the real datasets, producing real,
# full-accuracy artifacts baked into this image.
RUN python -m ml.pipeline.train_all

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
