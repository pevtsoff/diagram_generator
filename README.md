# AI Diagram Generation Service

An async, stateless Python API service that creates cloud architecture diagrams using AI agents powered by Large Language Models (LLM). Users can describe diagram components in natural language and receive rendered diagram images. The service provides both a REST API and a web-based chat interface powered by Chainlit.

## Features

- **Natural Language to Diagrams**: Convert text descriptions to cloud architecture diagrams
- **Multi-Cloud Support**: AWS, GCP, and Azure components
- **Assistant Interface**: Interactive chat for complex diagram creation workflows
- **Web Chat Interface**: Chainlit-powered web UI for easy diagram creation
- **Stateless Design**: No database or user sessions required
- **Async Architecture**: Built with FastAPI for high performance
- **Agent-Based**: Uses LLM-powered agents with custom tools
- **Containerized**: Docker support for easy deployment

## Supported Components

The service supports 17+ cloud component types:

### AWS Services
- **EC2**: Compute instances
- **RDS**: Managed database service
- **ALB/ELB**: Application/Elastic Load Balancers
- **SQS**: Simple Queue Service
- **S3**: Simple Storage Service
- **CloudWatch**: Monitoring and logging
- **Route53**: DNS service
- **IAM**: Identity and Access Management

### GCP Services
- **Compute Engine**: Virtual machines
- **GKE**: Google Kubernetes Engine
- **Cloud SQL**: Managed database
- **Load Balancer**: Traffic distribution

### Azure Services
- **Virtual Machines**: Compute instances
- **Azure SQL**: Database service
- **Load Balancer**: Traffic distribution

## Quick Start

### Prerequisites

- Python 3.13+
- UV package manager
- Docker & Docker Compose (for containerized deployment)
- Gemini API key (free at [Google AI Studio](https://makersuite.google.com/))

### Deployment Options Comparison

| Feature | Docker Compose | Native Installation |
|---------|----------------|-------------------|
| **Setup Complexity** | Simple (one command) | Moderate (requires system dependencies) |
| **System Requirements** | Docker only | Python 3.13+, Graphviz, UV |
| **Portability** | High (works everywhere) | Requires same environment |
| **Development** | Good | Excellent (hot reload) |
| **Resource Usage** | Higher (container overhead) | Lower (direct execution) |
| **Debugging** | Container logs | Direct process access |
| **Recommended For** | Production, quick demo | Development, customization |

### Option 1: Docker Compose (Recommended)

1. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   # This .env file will be used by both Docker and native deployments
   ```

2. **Build and Run Both Services**
   ```bash
   docker-compose up --build
   ```

3. **Access the Services**
   - **API Documentation**: http://localhost:8000/docs
   - **Chainlit Web UI**: http://localhost:8001
   - **API Health Check**: http://localhost:8000/api/health

### Option 2: Native Installation

#### Prerequisites for Native Installation

- **Python 3.13+**
- **UV package manager** (install from [uv.sh](https://uv.sh))
- **Graphviz** (required for diagram generation)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install graphviz graphviz-dev pkg-config
  
  # macOS
  brew install graphviz
  
  # Windows (using chocolatey)
  choco install graphviz
  ```

#### Step-by-Step Native Setup

1. **Clone and Setup Environment**
   ```bash
   git clone <repository-url>
   cd diagram_generator
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   # Note: Use the same .env file created for Docker deployment
   ```

2. **Install Dependencies**
   ```bash
   uv sync
   ```

3. **Launch Services**

   **Option A: Run Both Services (Recommended)**
   
   In separate terminals:
   
   **Terminal 1 - API Service:**
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   **Terminal 2 - Chainlit Web UI:**
   ```bash
   uv run chainlit run chainlit_app.py --host 0.0.0.0 --port 8001
   ```

   **Option B: Run Only Chainlit (Uses API Service)**
   
   If you have the API service running elsewhere or want to use a different API endpoint:
   ```bash
   # Set API URL in .env or environment
   export API_BASE_URL=http://localhost:8000
   uv run chainlit run chainlit_app.py --host 0.0.0.0 --port 8001
   ```

4. **Access the Services**
   - **API Documentation**: http://localhost:8000/docs
   - **Chainlit Web UI**: http://localhost:8001
   - **API Health Check**: http://localhost:8000/api/health

### Option 3: Development Mode

#### API Service Only (Development)

1. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   # Uses the same .env file as Docker deployment
   ```

2. **Install Dependencies**
   ```bash
   uv sync
   ```

3. **Run the API Service**
   ```bash
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

#### Chainlit Web UI (Development)

1. **Install Dependencies** (if not already done)
   ```bash
   uv sync
   ```

2. **Run Chainlit**
   ```bash
   uv run chainlit run chainlit_app.py --host 0.0.0.0 --port 8001
   ```

3. **Access Chainlit**
   - Web UI: http://localhost:8001

## Usage

### Web Interface (Chainlit)

The easiest way to create diagrams is through the Chainlit web interface:

1. **Open the Web UI**: Navigate to http://localhost:8001
2. **Start a Conversation**: Type your diagram request in natural language
3. **View Results**: The assistant will generate and display your diagram

**Example Requests:**
```
"Create a web application with load balancer and database"
"Design a microservices architecture with API gateway"
"Build a simple 3-tier architecture"
"Show me a diagram with User -> Nginx -> API -> Redis, and API -> Database"
```

### API Endpoints

#### `POST /api/generate-diagram`
Generate a diagram from natural language description.

**Request:**
```json
{
  "description": "Create a web app with load balancer, two EC2 instances, and RDS database"
}
```

**Response:**
```json
{
  "success": true,
  "image_url": "/api/images/diagram_123.png",
  "specification": {
    "name": "Web Application Architecture",
    "nodes": [...],
    "connections": [...],
    "clusters": [...]
  },
  "message": "Diagram generated successfully"
}
```

#### `POST /api/assistant-chat` (Bonus)
Interactive assistant for complex workflows.

**Request:**
```json
{
  "message": "How do I design a microservices architecture?"
}
```

**Response:**
```json
{
  "type": "text",
  "response": "For microservices architecture, consider...",
  "supported_node_types": ["ec2", "rds", "alb", ...]
}
```

#### `GET /api/health`
Service health check.

#### `GET /api/supported-components`
List all supported diagram components.

## Example Usage

### Example 1: Basic Web Application

**Input:**
```
Create a diagram showing a basic web application with an Application Load Balancer, 
two EC2 instances for the web servers, and an RDS database for storage. 
The web servers should be in a cluster named 'Web Tier'.
```

**Generated Architecture:**
- Application Load Balancer → Web Tier Cluster (2 × EC2) → RDS Database

### Example 2: Microservices Architecture

**Input:**
```
Design a microservices architecture with three services: an authentication service, 
a payment service, and an order service. Include an API Gateway for routing, 
an SQS queue for message passing between services, and a shared RDS database. 
Group the services in a cluster called 'Microservices'. Add CloudWatch for monitoring.
```

**Generated Architecture:**
- ALB (API Gateway) → Microservices Cluster (Auth, Payment, Order) → RDS + SQS + CloudWatch

### Example 3: Using Chainlit Web UI

**Step 1**: Open http://localhost:8001 in your browser

**Step 2**: Type your request:
```
"Create me this diagram - User -> Nginx -> API -> Redis, and API -> Database"
```

**Step 3**: The assistant will generate and display the diagram with:
- User → Nginx (Load Balancer)
- Nginx → API Server
- API Server → Redis Cache
- API Server → Database

## Architecture

### Components

The service consists of several key components:

1. **FastAPI Application** (`main.py`): REST API service
2. **Chainlit Application** (`chainlit_app.py`): Web chat interface
3. **DiagramAgent**: Main orchestrator for diagram creation
4. **DiagramTools**: Wrapper around the `diagrams` package
5. **GeminiClient**: LLM integration with visible prompt logic
6. **DiagramAgentPool**: Manages concurrent requests

### Agent System

The service uses a multi-agent architecture:

1. **DiagramAgent**: Main orchestrator
2. **DiagramTools**: Wrapper around the `diagrams` package
3. **GeminiClient**: LLM integration with visible prompt logic
4. **DiagramAgentPool**: Manages concurrent requests

### Prompt Engineering

All LLM prompts are visible and documented in the code (not hidden behind opaque frameworks):

```python
def _build_diagram_generation_prompt(self, user_description: str, supported_node_types: List[str]) -> str:
    """Build the prompt for diagram generation - visible prompt logic as required."""
    
    prompt_template = """
    You are a cloud architecture diagram expert. Your task is to analyze a user's description 
    and create a structured diagram specification.
    
    SUPPORTED NODE TYPES: {node_types}
    USER DESCRIPTION: "{description}"
    
    INSTRUCTIONS:
    1. Analyze the user's description and identify the components needed
    2. Map each component to one of the supported node types
    3. Create connections between components based on logical relationships
    4. Group related components into clusters when appropriate
    5. Return a valid JSON structure with the exact schema below
    ...
    """
```

### Stateless Design

- No database or persistent storage
- No user sessions
- Temporary files are automatically cleaned up
- Each request is independent

## Configuration

### Environment Variables

The project uses a single `.env` file for both Docker and native deployments. This ensures consistency and makes it easy to switch between deployment methods.

#### Required Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Optional Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=false

# Agent Configuration
AGENT_POOL_SIZE=3

# Logging
LOG_LEVEL=INFO

# Development/Testing
USE_MOCK_LLM=false  # Set to true for testing without API key

# Storage Configuration
IMAGES_DIR=./diagram_service_images  # Directory for storing generated diagrams

# Chainlit-specific (optional)
CHAINLIT_HOST=0.0.0.0
CHAINLIT_PORT=8001
API_BASE_URL=http://localhost:8000  # URL of the API service
```

#### Environment File Setup
1. Copy the example file: `cp .env.example .env`
2. Edit `.env` and add your `GEMINI_API_KEY`
3. The same `.env` file works for both Docker and native deployments

### Docker vs Native Configuration

#### Docker Deployment
- Environment variables are loaded from `.env` file (same as native)
- Services communicate via Docker network
- Volumes are mounted for persistent storage
- Health checks are automatically configured

#### Native Deployment
- Environment variables are loaded from `.env` file (same as Docker)
- Services communicate via localhost
- Temporary files are stored in local filesystem
- Manual process management required

#### Shared Configuration
Both Docker and native deployments use the same `.env` file, making it easy to switch between deployment methods without reconfiguring environment variables.

### Agent Pool Configuration

The service uses an agent pool to handle concurrent requests efficiently:

- Default pool size: 3 agents
- Stateless agents (created per request)
- Automatic cleanup and resource management

## Development

### Running Tests

```bash
uv run pytest tests/
```

### Project Structure

```
diagram-service/
├── diagram_service/
│   ├── agents/          # Agent system
│   ├── tools/           # Diagram creation tools
│   ├── llm/             # LLM integration
│   └── api/             # FastAPI routes
├── tests/               # Unit tests
├── main.py              # FastAPI application entry point
├── chainlit_app.py      # Chainlit web UI entry point
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-container setup
└── README.md            # This file
```

### Adding New Node Types

1. Add the component import to `diagram_service/tools/diagram_tools.py`
2. Add to `supported_node_types` dictionary
3. Add description to `get_node_description()` method

Example:
```python
from diagrams.aws.analytics import EMR

# In DiagramTools.__init__():
self.supported_node_types = {
    # ... existing types ...
    "emr": EMR,
}
```

## Error Handling

The service includes comprehensive error handling:

- **LLM Errors**: Graceful fallbacks and error messages
- **Diagram Generation**: Validation and error recovery
- **File Cleanup**: Automatic temporary file management
- **Health Checks**: Built-in service monitoring

## Limitations and Considerations

### Current Limitations

1. **Diagram Complexity**: Very complex diagrams may hit LLM context limits
2. **Component Coverage**: Limited to pre-defined cloud components
3. **Layout Control**: Automatic layout only (no manual positioning)
4. **File Storage**: Temporary file approach (production would use cloud storage)

### Production Considerations

1. **File Storage**: Implement proper cloud storage (S3, GCS, etc.)
2. **Caching**: Add Redis for LLM response caching
3. **Rate Limiting**: Implement API rate limiting
4. **Monitoring**: Add comprehensive observability
5. **Security**: API authentication and input validation
6. **Scaling**: Kubernetes deployment and horizontal scaling

### Security Notes

- Input validation on all endpoints
- Temporary file cleanup to prevent disk filling
- No user data persistence (stateless design)
- Container runs as non-root user

## API Examples

### Using curl

```bash
# Generate a diagram
curl -X POST "http://localhost:8000/api/generate-diagram" \
  -H "Content-Type: application/json" \
  -d '{"description": "Create a simple web app with load balancer and database"}'

# Chat with assistant
curl -X POST "http://localhost:8000/api/assistant-chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What components do I need for a scalable web application?"}'

# Check health
curl "http://localhost:8000/api/health"
```

### Using Python

```python
import requests

# Generate diagram
response = requests.post(
    "http://localhost:8000/api/generate-diagram",
    json={"description": "Create a microservices architecture with API gateway"}
)
result = response.json()
print(f"Diagram URL: {result['image_url']}")
```

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not set"**
   - Solution: Add your Gemini API key to `.env` file (same file for Docker and native)
   - Alternative: Set `USE_MOCK_LLM=true` for testing

2. **"graphviz not found"**
   - Solution: Install graphviz system package
   - Ubuntu/Debian: `apt-get install graphviz graphviz-dev pkg-config`
   - macOS: `brew install graphviz`
   - Windows: `choco install graphviz`

3. **"Port 8000 already in use"**
   - Solution: Change PORT in `.env` or stop conflicting service
   - Alternative: Use different port: `uv run uvicorn main:app --port 8002`

4. **"Port 8001 already in use" (Chainlit)**
   - Solution: Change Chainlit port or stop conflicting service
   - Alternative: Use different port: `uv run chainlit run chainlit_app.py --port 8002`

5. **Docker build fails**
   - Solution: Ensure Docker has enough memory (>2GB recommended)
   - Check Docker logs: `docker-compose logs`

6. **Chainlit not starting**
   - **Native**: Check if all dependencies are installed: `uv sync`
   - **Docker**: Check logs: `docker-compose logs chainlit`
   - **Common fix**: Ensure graphviz is installed (see issue #2)

7. **"Module not found" errors**
   - **Native**: Run `uv sync` to install dependencies
   - **Docker**: Rebuild containers: `docker-compose build --no-cache`

8. **Chainlit can't connect to API service**
   - **Docker**: Ensure both services are running: `docker-compose ps`
   - **Native**: Check if API service is running on port 8000
   - **Network**: Verify no firewall blocking localhost connections

### Logs

Check application logs for detailed error information:

```bash
# Native development
uv run uvicorn main:app --log-level debug
uv run chainlit run chainlit_app.py --log-level debug

# Docker
docker-compose logs -f diagram-service
docker-compose logs -f chainlit

# Docker (individual service)
docker-compose logs -f chainlit
docker-compose logs -f diagram-service
```

### Docker-Specific Commands

```bash
# Start services in background
docker-compose up -d

# View running services
docker-compose ps

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up --build

# View logs for specific service
docker-compose logs -f chainlit

# Access container shell (for debugging)
docker-compose exec chainlit bash
docker-compose exec diagram-service bash
```

## License

This project is created as a home assignment demonstration.

## Support

For questions or issues, check the API documentation at `/docs` endpoint or review the application logs. 