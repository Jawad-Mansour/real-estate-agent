PHASE 11: DOCKER CONTAINERIZATION - COMPLETE DOCUMENTATION
==========================================================

DATE COMPLETED: April 16, 2026

================================================================================
WHAT IS DOCKER?
================================================================================

Docker is a containerization platform that packages an application and its
dependencies into a standardized unit called a container. This ensures the
application runs the same way on any system (development, testing, production).

================================================================================
WHY DOCKER FOR THIS PROJECT?
================================================================================

| Reason | Explanation |
|--------|-------------|
| PDF #10 Requirement | "Write a Dockerfile from scratch" |
| Reproducibility | Anyone can run the app with one command |
| Deployment | Easy deployment on Railway, AWS, GCP |
| Isolation | Dependencies don't conflict with host system |

================================================================================
FILE STRUCTURE
================================================================================

real-estate-agent/
├── docker/
│   ├── Dockerfile           # Production build
│   ├── Dockerfile.dev       # Development with hot-reload
│   └── docker-compose.yml   # Multi-service orchestration
├── .dockerignore            # Exclude unnecessary files
├── requirements.txt         # Python dependencies
├── backend/                 # Application code
├── frontend/                # Static files
└── .env                     # Environment variables (not in Git)

================================================================================
DOCKERFILE EXPLANATION (Line by Line)
================================================================================

LINE 1-2: Multi-stage build comment
# ============================================================
# STAGE 1: Builder - Install dependencies
# ============================================================

LINE 4: Base image for builder
FROM python:3.11-slim as builder
- Uses official Python 3.11 slim image (smaller than full image)
- Names this stage "builder" for reference later

LINE 7: Set working directory
WORKDIR /app
- All subsequent commands run from /app directory

LINE 10-13: Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*
- gcc/g++ needed to compile numpy/pandas
- Clean up apt cache to reduce image size

LINE 16-17: Copy requirements file
COPY requirements.txt .
- Copied first for Docker caching (if requirements don't change, this layer is cached)

LINE 20-21: Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
- --no-cache-dir reduces image size
- Installs all packages from requirements.txt

LINE 25-26: Runtime stage
FROM python:3.11-slim
- Fresh slim image for final container (no build tools)

LINE 29: Set working directory
WORKDIR /app

LINE 32-34: Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
- Copies only the installed packages, not the build tools
- Results in smaller final image (~200MB vs ~600MB)

LINE 37-39: Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
- Copies backend and frontend code

LINE 42-43: Copy model artifacts
COPY backend/models/ ./backend/models/
- Copies trained model and preprocessor

LINE 46: Expose port
EXPOSE 8000
- Informs Docker that container listens on port 8000

LINE 49-51: Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
- Docker checks if app is healthy every 30 seconds
- Uses curl to call /health endpoint
- If fails, container is marked unhealthy

LINE 54: Start command
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
- Starts FastAPI with uvicorn
- Listens on all interfaces (0.0.0.0) so accessible from outside container

================================================================================
MULTI-STAGE BUILD BENEFITS
================================================================================

| Single-stage | Multi-stage (Our choice) |
|--------------|-------------------------|
| Includes compilers (gcc, g++) | Compilers only in builder |
| Image size: ~600MB | Image size: ~200MB |
| Slower to download/deploy | Faster to download/deploy |
| More attack surface | Smaller attack surface |

================================================================================
DOCKER-COMPOSE.YML EXPLANATION
================================================================================

version: '3.8'
- Docker Compose file format version

services:
  housewise:
    - Service name

    build:
      context: ..
      dockerfile: docker/Dockerfile
    - Build context is parent directory (where requirements.txt is)
    - Uses Dockerfile from docker/ folder

    container_name: housewise-app
    - Name of the running container

    ports:
      - "8000:8000"
    - Maps host port 8000 to container port 8000

    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    - Passes GROQ_API_KEY from host to container

    env_file:
      - ../.env
    - Loads environment variables from .env file

    restart: unless-stopped
    - Automatically restarts unless manually stopped

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    - Same healthcheck as Dockerfile

================================================================================
.DOCKERIGNORE EXPLANATION
================================================================================

Excluded patterns and why:

| Pattern | Why Excluded |
|---------|---------------|
| __pycache__/ | Python cache files (not needed) |
| .venv/ | Local virtual environment (container has its own) |
| .env | Contains secrets (passed via --env-file) |
| logs/ | Application logs (not needed in image) |
| .git/ | Git history (not needed) |
| docs/ | Documentation (not needed to run) |
| notebooks/ | Jupyter notebooks (not needed) |
| data/raw/*.csv | Raw data (large, not needed) |
| *.ipynb | Notebook files |

================================================================================
DOCKER COMMANDS REFERENCE
================================================================================

| Command | Purpose |
|---------|---------|
| docker build -f docker/Dockerfile -t housewise:latest . | Build image |
| docker images | List images |
| docker run -d -p 8000:8000 --name housewise-app housewise:latest | Run container |
| docker ps | List running containers |
| docker logs housewise-app | View container logs |
| docker stop housewise-app | Stop container |
| docker start housewise-app | Start stopped container |
| docker rm housewise-app | Remove container |
| docker rmi housewise:latest | Remove image |
| docker-compose up -d | Start with compose |
| docker-compose down | Stop with compose |

================================================================================
RUNNING THE APPLICATION
================================================================================

1. Build the image:
   docker build -f docker/Dockerfile -t housewise:latest .

2. Run the container:
   docker run -d -p 8000:8000 --name housewise-app -e GROQ_API_KEY=$GROQ_API_KEY housewise:latest

3. Check logs:
   docker logs housewise-app

4. Test the API:
   curl http://localhost:8000/health

5. Access the frontend:
   http://localhost:8000 (FastAPI serves static files)

================================================================================
TROUBLESHOOTING
================================================================================

| Problem | Solution |
|---------|----------|
| Port already in use | Change port mapping: -p 8001:8000 |
| Container exits immediately | Check logs: docker logs housewise-app |
| GROQ_API_KEY not found | Pass via -e flag or .env file |
| Model file not found | Ensure backend/models/ exists |
| curl: command not found in HEALTHCHECK | Install curl: RUN apt-get update && apt-get install -y curl |

================================================================================
DEPLOYMENT ON RAILWAY
================================================================================

1. Push code to GitHub:
   git add .
   git commit -m "Add Docker configuration"
   git push origin master

2. Go to railway.app
3. Sign in with GitHub
4. Click "New Project" → "Deploy from GitHub repo"
5. Select your repository
6. Railway auto-detects Dockerfile
7. Add environment variable: GROQ_API_KEY
8. Click "Deploy"

================================================================================
PDF REQUIREMENTS MET
================================================================================

| # | Requirement | How Phase 11 Satisfies |
|---|-------------|------------------------|
| 10 | FastAPI + Docker | Dockerfile created, model loads at startup |
| 10 | Write Dockerfile from scratch | Custom multi-stage Dockerfile |
| 10 | Image includes trained model | COPY backend/models/ |
| 10 | Accessible from outside | PORT mapping, host 0.0.0.0 |

================================================================================
NEXT STEPS (Phase 12 & 13)
================================================================================

Phase 12: Prompt Versioning Documentation
- Document prompt comparison results
- Log winner with evidence

Phase 13: Testing & Final Validation
- Run final validation script
- Prepare project header
- Deploy on Railway

================================================================================
