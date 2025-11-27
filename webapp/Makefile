.PHONY: help setup install dev run test clean deploy

# Default target
help:
	@echo "Agent Lucy Web App - Available commands:"
	@echo ""
	@echo "  make setup      - Initial setup (install uv, create venv)"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Run development server with hot reload"
	@echo "  make run        - Run production server"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean up temporary files"
	@echo "  make deploy     - Deploy to Cloudflare Pages"
	@echo "  make docker     - Build and run Docker container"
	@echo ""

# Initial setup
setup:
	@echo "📦 Setting up Agent Lucy Web App..."
	@if ! command -v uv &> /dev/null; then \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@echo "Creating virtual environment..."
	cd .. && uv venv .venv
	@echo "✅ Setup complete!"
	@echo "💡 Run 'source ../.venv/bin/activate' to activate the virtual environment"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	cd .. && uv pip install -r webapp/requirements.txt
	@echo "✅ Dependencies installed!"

# Install for development
install-dev: install
	@echo "📦 Installing development dependencies..."
	cd .. && uv pip install pytest pytest-asyncio pytest-cov httpx
	@echo "✅ Development dependencies installed!"

# Run development server with hot reload
dev:
	@echo "🚀 Starting development server on http://localhost:8001"
	@echo "📝 Hot reload enabled - edit files and see changes instantly"
	@echo "🛑 Press Ctrl+C to stop"
	cd .. && uv run uvicorn webapp.api.main:app --host 0.0.0.0 --port 8001 --reload

# Run production server
run:
	@echo "🚀 Starting production server on http://localhost:8001"
	@echo "🛑 Press Ctrl+C to stop"
	cd .. && uv run uvicorn webapp.api.main:app --host 0.0.0.0 --port 8001

# Run in background
run-bg:
	@echo "🚀 Starting server in background on http://localhost:8001"
	cd .. && uv run uvicorn webapp.api.main:app --host 0.0.0.0 --port 8001 > logs/webapp.log 2>&1 &
	@echo "📝 Logs: logs/webapp.log"
	@echo "🛑 To stop: make stop"

# Stop background server
stop:
	@echo "🛑 Stopping server..."
	@pkill -f "uvicorn webapp.api.main:app" || true
	@echo "✅ Server stopped"

# Run tests
test:
	@echo "🧪 Running tests..."
	cd .. && uv run pytest webapp/tests/ -v

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	cd .. && uv run pytest webapp/tests/ -v --cov=webapp --cov-report=html
	@echo "📊 Coverage report: htmlcov/index.html"

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
	@echo "✅ Cleaned up!"

# Deploy to Cloudflare Pages
deploy:
	@echo "🚀 Deploying to Cloudflare Pages..."
	@if ! command -v wrangler &> /dev/null; then \
		echo "❌ Wrangler not found. Install with: npm install -g wrangler"; \
		exit 1; \
	fi
	wrangler pages deploy public --project-name agent-lucy-webapp
	@echo "✅ Deployed!"

# Build Docker image
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t agent-lucy-webapp .
	@echo "✅ Docker image built!"

# Run Docker container
docker-run: docker-build
	@echo "🐳 Running Docker container..."
	docker run -p 8001:8000 --env-file ../.env agent-lucy-webapp

# Docker compose (if you add docker-compose.yml)
docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo "✅ Services started!"

docker-down:
	@echo "🐳 Stopping Docker services..."
	docker-compose down
	@echo "✅ Services stopped!"

# Open in browser
open:
	@echo "🌐 Opening web app in browser..."
	@open http://localhost:8001 || xdg-open http://localhost:8001 || start http://localhost:8001

# Show logs
logs:
	@tail -f logs/webapp.log

# Health check
health:
	@echo "🏥 Checking health..."
	@curl -s http://localhost:8001/api/health | jq . || curl -s http://localhost:8001/api/health

# List all agents
list-agents:
	@echo "🤖 Listing agents..."
	cd .. && uv run python -c "from azure.identity import DefaultAzureCredential; from azure.ai.projects import AIProjectClient; client = AIProjectClient(endpoint='https://sjliao-8193-resource.services.ai.azure.com/api/projects/sjliao-8193', credential=DefaultAzureCredential()); [print(f'{a.name} ({a.model})') for a in client.agents.list_agents()]"

# Format code
format:
	@echo "🎨 Formatting code..."
	cd .. && uv run black webapp/
	cd .. && uv run ruff check --fix webapp/
	@echo "✅ Code formatted!"

# Lint code
lint:
	@echo "🔍 Linting code..."
	cd .. && uv run ruff check webapp/
	cd .. && uv run mypy webapp/
	@echo "✅ Linting complete!"

# Create logs directory
logs-dir:
	@mkdir -p logs

# Full setup and run
quickstart: setup install dev

# Production ready
production: install test run
