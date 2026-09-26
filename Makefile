.PHONY: help install run run-backend run-frontend test test-backend test-frontend lint build clean

help:
	@echo "Mentis-Q QDS Security Framework Commands:"
	@echo "  make install        - Install backend & frontend dependencies"
	@echo "  make run            - Run backend and frontend concurrently (via run.py)"
	@echo "  make run-backend    - Run FastAPI backend on port 8000"
	@echo "  make run-frontend   - Run Vite frontend on port 5173"
	@echo "  make test           - Run full backend test suite"
	@echo "  make test-frontend  - Run frontend typecheck and linter"
	@echo "  make build          - Build production frontend bundle"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

run:
	python run.py

run-backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

test: test-backend

test-backend:
	cd backend && python -m pytest -v

test-frontend:
	cd frontend && npx tsc -b && npx oxlint

build:
	cd frontend && npm run build

clean:
	rm -rf frontend/dist .pytest_cache backend/.pytest_cache
