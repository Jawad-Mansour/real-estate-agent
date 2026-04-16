FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies (no apt-get needed)
RUN pip install --no-cache-dir \
    numpy==1.26.0 \
    pandas==2.1.4 \
    scikit-learn==1.4.2 \
    fastapi==0.115.0 \
    uvicorn==0.32.0 \
    pydantic==2.9.0 \
    joblib==1.3.2 \
    python-dotenv==1.0.0 \
    httpx==0.27.0 \
    groq==0.9.0

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY backend/models/ ./backend/models/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
