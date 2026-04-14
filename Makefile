.PHONY: install dev test docker-build docker-run

install:
	uv add -r requirements.txt

dev:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest backend/tests/ -v

docker-build:
	docker build -f docker/Dockerfile -t real-estate-agent .

docker-run:
	docker run -p 8000:8000 real-estate-agent

frontend:
	cd frontend && python -m http.server 3000
