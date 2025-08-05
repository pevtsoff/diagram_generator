# This is an example of project, generated completely by Cusros.AI with my guidence, within several hours

# AI Diagram Generation Service

An async Python API service that creates cloud architecture diagrams using AI agents. Users describe diagram components in natural language and receive rendered diagram images. Includes both REST API and Chainlit web interface.

## Features

- **Natural Language to Diagrams**: Convert text descriptions to cloud architecture diagrams
- **Multi-Cloud Support**: AWS, GCP, and Azure components
- **Web Chat Interface**: Chainlit-powered web UI
- **Stateless Design**: No database required
- **Containerized**: Docker support for easy deployment

## Quick Start

### Prerequisites

- Python 3.13+ & UV package manager
- Docker & Docker Compose (for containerized deployment)
- Gemini API key (free at [Google AI Studio](https://makersuite.google.com/))

### Option 1: Docker Compose (Recommended)

```bash
# Setup
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run
docker-compose up --build

# Access
# API: http://localhost:8000/docs
# Chainlit: http://localhost:8001
```

### Option 2: Native Installation

```bash
# Install system dependencies
# Ubuntu/Debian: sudo apt-get install graphviz graphviz-dev pkg-config
# macOS: brew install graphviz

# Setup
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Install dependencies
uv sync

# Run (in separate terminals)
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
uv run chainlit run chainlit_app.py --host 0.0.0.0 --port 8001
```

## Usage

### Web Interface (Chainlit)

1. Open <http://localhost:8001>
2. Describe your diagram in natural language
3. View the generated diagram

**Example Requests:**

```
"Create a web application with load balancer and database"
"Design a microservices architecture with API gateway"
"Show me User -> Nginx -> API -> Redis, and API -> Database"
```

### API Endpoints

#### `POST /api/generate-diagram`

```json
{
  "description": "Create a web app with load balancer, two EC2 instances, and RDS database"
}
```

#### `POST /api/assistant-chat`

Interactive assistant for complex workflows.

#### `GET /api/health`

Service health check.

## Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
HOST=0.0.0.0
PORT=8000
AGENT_POOL_SIZE=3
LOG_LEVEL=INFO
USE_MOCK_LLM=false
IMAGES_DIR=./diagram_service_images
```

**Note**: The same `.env` file works for both Docker and native deployments.

## Supported Components

### AWS Services

EC2, RDS, ALB/ELB, SQS, S3, CloudWatch, Route53, IAM

### GCP Services

Compute Engine, GKE, Cloud SQL, Load Balancer

### Azure Services

Virtual Machines, Azure SQL, Load Balancer

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not set"**
   - Add your Gemini API key to `.env` file
   - Or set `USE_MOCK_LLM=true` for testing

2. **"graphviz not found"**
   - Install graphviz: `sudo apt-get install graphviz` (Ubuntu) or `brew install graphviz` (macOS)

3. **Port conflicts**
   - Change ports in `.env` or use different ports: `--port 8002`

4. **Docker issues**
   - Check logs: `docker-compose logs`
   - Rebuild: `docker-compose up --build`

## Development

### Running Tests

```bash
uv run pytest tests/
```

### Project Structure

```
diagram_generator/
├── diagram_service/     # Core service components
├── main.py             # FastAPI application
├── chainlit_app.py     # Chainlit web UI
├── docker-compose.yml  # Docker setup
└── tests/              # Unit tests
```

## API Examples

### Using curl

```bash
# Generate diagram
curl -X POST "http://localhost:8000/api/generate-diagram" \
  -H "Content-Type: application/json" \
  -d '{"description": "Create a simple web app with load balancer and database"}'

# Check health
curl "http://localhost:8000/api/health"
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/generate-diagram",
    json={"description": "Create a microservices architecture"}
)
result = response.json()
print(f"Diagram URL: {result['image_url']}")
```

## Architecture

- **FastAPI Application**: REST API service
- **Chainlit Application**: Web chat interface
- **DiagramAgent**: Main orchestrator for diagram creation
- **DiagramTools**: Wrapper around the `diagrams` package
- **GeminiClient**: LLM integration with visible prompt logic

## Limitations

- Diagram complexity limited by LLM context
- Automatic layout only (no manual positioning)
- Temporary file storage (production would use cloud storage)

## License

This project is created as a home assignment demonstration.
