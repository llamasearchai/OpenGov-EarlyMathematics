<p align="center">
  <img src="assets/logo.svg" alt="OpenGov EarlyMathematics" width="520" />
</p>

<p align="center">
  <a href="https://github.com/llamasearchai/OpenGov-EarlyMathematics/actions/workflows/ci.yml">
    <img src="https://github.com/llamasearchai/OpenGov-EarlyMathematics/actions/workflows/ci.yml/badge.svg" alt="CI" />
  </a>
  <img src="https://img.shields.io/badge/coverage-100%25-brightgreen" alt="Coverage" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License" />
</p>

# OpenGov-EarlyMathematics

AI-powered personalized mathematics education platform for K-12 students.

## Overview

OpenGov-EarlyMathematics is a comprehensive educational platform that leverages artificial intelligence to provide personalized mathematics learning experiences for students from kindergarten through high school. The platform combines adaptive learning algorithms, AI tutoring, and interactive content to create engaging and effective mathematics education.

## Features

### For Students
- **Personalized Learning Paths**: AI-driven curriculum adaptation based on individual progress and learning style
- **Interactive Lessons**: Engaging visual and interactive math content with step-by-step guidance
- **Real-time Feedback**: Instant feedback on problems with detailed explanations
- **Adaptive Practice**: Problems that adjust difficulty based on student performance
- **Progress Tracking**: Comprehensive analytics and achievement system
- **Multi-modal Learning**: Support for visual, auditory, and kinesthetic learning styles

### For Teachers
- **Class Management**: Tools for managing multiple students and classes
- **Assessment Tools**: Automated grading and performance analysis
- **Lesson Planning**: AI-assisted lesson plan generation
- **Student Analytics**: Detailed progress tracking and insights
- **Assignment Management**: Create and manage assignments with ease

### For Parents
- **Progress Dashboard**: Real-time view of child's learning progress
- **Performance Reports**: Weekly and monthly progress summaries
- **Learning Goals**: Set and track learning objectives together
- **Communication Tools**: Direct messaging with teachers and administrators

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Student Interface                      │
│              (Web App / Mobile App)                      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    API Gateway                          │
│                 (FastAPI + WebSocket)                   │
└──────────┬───────────┬───────────┬─────────────────────┘
           │           │           │
    ┌──────▼────┐ ┌───▼────┐ ┌───▼────┐
    │ Learning  │ │Problem │ │  AI    │
    │   Path    │ │ Engine │ │ Tutor  │
    └───────────┘ └────────┘ └────────┘
           │           │           │
    ┌──────▼───────────▼───────────▼─────┐
    │       ML/AI Services Layer         │
    │   (Assessment, Adaptation, NLP)    │
    └─────────────────────────────────────┘
                       │
    ┌──────────────────▼─────────────────┐
    │          Data Layer                │
    │   (PostgreSQL, Redis, SQLite)      │
    └─────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy, Redis
- **AI/ML**: OpenAI Agents SDK, Ollama, scikit-learn, NumPy
- **Data**: PostgreSQL, SQLite, Datasette, sqlite-utils
- **Frontend**: Streamlit, Textual (TUI)
- **DevOps**: Docker, uv, tox, hatch, GitHub Actions
- **Quality**: Ruff, Black, isort, MyPy, Bandit, pre-commit

## Quick Start

### Using uv (Recommended)

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/opengov/earlymathematics.git
cd opengov-earlymathematics

# Install dependencies
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
uv run python -c "from src.opengov_earlymathematics.agents.data_client import MathDataClient; MathDataClient()._initialize_tables()"

# Start the API server
uv run hatch run serve

# Launch student interface (new terminal)
uv run streamlit run src/opengov_earlymathematics/ui/app.py

# Launch terminal interface (new terminal)
uv run hatch run tui
```

### Using Docker Compose

```bash
# Build and run with Docker Compose
docker compose up -d

# Access the application
open http://localhost:8000  # API
open http://localhost:8501  # Student UI
open http://localhost:9000  # Datasette
open http://localhost:11434 # Ollama API
```

### Using virtualenv

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Run tests
pytest -q

# Start API server
uvicorn src.opengov_earlymathematics.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/mathdb
REDIS_URL=redis://localhost:6379/0

# OpenAI Integration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Ollama (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434

# Educational Settings
MAX_DAILY_PRACTICE_TIME=120
BREAK_REMINDER_INTERVAL=30
MIN_ACCURACY_FOR_ADVANCEMENT=0.8
```

## CLI Usage

### Basic Commands

```bash
# Show version
uv run hatch run version

# Explore curriculum
uv run hatch run curriculum --grade 3

# Generate practice problem
uv run hatch run generate-problem --topic multiplication --difficulty 2 --grade 3

# Check solution
uv run hatch run check-solution --problem-id prob_123 --answer 42

# Run demo
uv run hatch run demo
```

### LLM Integration

```bash
# Use local Ollama models
llm -m ollama:llama2 "Explain fractions to a 3rd grader"

# Use OpenAI via llm tool
llm -m gpt-4 "Create a lesson plan for multiplication"

# Browse data with Datasette
datasette serve data/math_education.db -p 9000
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv sync --dev

# Set up pre-commit hooks
uv run pre-commit install

# Run all quality checks
uv run hatch run all

# Run specific test types
uv run hatch run test-unit
uv run hatch run test-integration
uv run hatch run test-e2e
uv run hatch run test-property
uv run hatch run test-benchmark
```

### Code Quality

```bash
# Format code
uv run hatch run fmt

# Lint code
uv run hatch run lint

# Type checking
uv run hatch run type

# Security scan
uv run hatch run security

# All quality checks
uv run hatch run quality
```

### Testing

```bash
# Run all tests
uv run pytest -q

# Run with coverage
uv run pytest --cov=src/opengov_earlymathematics

# Run specific test categories
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m e2e

# Property-based testing
uv run pytest tests/property/

# Performance benchmarks
uv run pytest tests/benchmarks/ --benchmark-only
```

## OpenAI Agents Integration

The platform integrates with OpenAI Agents SDK for advanced AI capabilities:

```python
from src.opengov_earlymathematics.agents.math_agent import MathAgent

# Initialize agent
agent = MathAgent()

# Generate personalized problem
problem = await agent.generate_problem(
    topic="fractions",
    difficulty_level=2,
    student_level=4
)

# Get AI tutoring
response = await agent.chat_with_student(
    student_id="student_123",
    message="I don't understand fractions"
)
```

## Ollama Integration

For local LLM operations:

```python
from src.opengov_earlymathematics.agents.ollama_client import OllamaMathClient

# Initialize client
client = OllamaMathClient()

# Generate explanation
explanation = client.explain_math_concept(
    concept="multiplication",
    grade_level=3,
    learning_style="visual"
)

# Create practice problem
problem = client.generate_practice_problem(
    topic="division",
    difficulty="intermediate",
    grade_level=4
)
```

## Datasette Integration

For data exploration and workflows:

```python
from src.opengov_earlymathematics.agents.data_client import MathDataClient

# Initialize data client
data_client = MathDataClient()

# Get student progress
progress = data_client.get_student_progress("student_123")

# Export data
json_data = data_client.export_student_data("student_123", format="json")

# Start Datasette server
data_client.start_datasette_server(port=9000)
```

## API Reference

### Core Endpoints

- `GET /health` - Health check
- `GET /` - API information
- `GET /api/v1/curriculum/grades/{grade}/topics` - Get topics for grade
- `GET /api/v1/curriculum/topics/{topic}/lessons` - Get lessons for topic
- `POST /api/v1/problems/generate` - Generate math problem
- `POST /api/v1/problems/check-solution` - Check student solution
- `POST /api/v1/learning-paths/create` - Create learning path
- `GET /api/v1/learning-paths/{path_id}` - Get learning path
- `POST /api/v1/tutoring/start-session` - Start AI tutoring session
- `POST /api/v1/tutoring/ask` - Ask AI tutor question
- `GET /api/v1/students/{student_id}/progress` - Get student progress
- `GET /api/v1/analytics/overview` - Get platform analytics

### Authentication

Currently supports API key authentication. JWT token support planned for future releases.

## Deployment

### Production Deployment

```bash
# Build production image
docker build --target runtime -t opengov/earlymathematics:latest .

# Run with Docker Compose
docker compose -f docker/compose.yml up -d

# Or run standalone
docker run --rm -p 8000:8000 opengov/earlymathematics:latest
```

### Kubernetes Deployment

```yaml
# Example deployment manifest
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opengov-math-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: opengov-math-api
  template:
    metadata:
      labels:
        app: opengov-math-api
    spec:
      containers:
      - name: api
        image: opengov/earlymathematics:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
```

## Monitoring and Observability

### Metrics Collection

The platform exposes Prometheus metrics at `/metrics` endpoint including:
- Request latency and throughput
- Error rates by endpoint
- Student engagement metrics
- AI model performance

### Logging

Structured logging with configurable levels:
- Development: Human-readable format
- Production: JSON format for log aggregation

### Health Checks

- API health: `GET /health`
- Database connectivity
- Redis connectivity
- Ollama service status

## Security

### Data Protection
- No hardcoded secrets
- Environment variable configuration
- Secure API key management
- Data encryption at rest and in transit

### Compliance
- Student data protection compliance
- FERPA considerations for educational data
- GDPR compliance for EU users

### Security Scanning
- Automated vulnerability scanning with Trivy
- Dependency security checks with Safety
- Code security analysis with Bandit

## Performance

### Benchmarks

Run performance benchmarks:

```bash
uv run pytest tests/benchmarks/ --benchmark-only --benchmark-sort=mean
```

### Optimization Features
- Response caching with Redis
- Database query optimization
- AI model response caching
- Static asset optimization

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure dependencies are installed
uv sync --dev

# Check Python version
python --version  # Should be >= 3.9
```

**API Connection Issues**
```bash
# Check API server status
curl http://localhost:8000/health

# Verify environment variables
echo $OPENAI_API_KEY  # Should not be empty
```

**Ollama Issues**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Pull required models
ollama pull llama2
ollama pull nomic-embed-text
```

**Database Issues**
```bash
# Check database connectivity
python -c "import sqlite3; sqlite3.connect('data/math_education.db')"

# Reset database
rm data/math_education.db
python -c "from src.opengov_earlymathematics.agents.data_client import MathDataClient; MathDataClient()._initialize_tables()"
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the full test suite
6. Submit a pull request

### Code Standards

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use type hints for all public functions

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting guide above
- Review the API documentation at `/docs`

## Acknowledgments

Built with cutting-edge educational technology:
- OpenAI GPT-4 for intelligent tutoring
- Ollama for local LLM capabilities
- Adaptive learning algorithms
- Evidence-based pedagogical approaches
- Modern Python ecosystem tools

---

**Repository Topics**: ai, llm, ollama, openai-agents, agents, datasette, sqlite, sqlite-utils, cli, tui, python, uv, tox, hatch, docker, devtools
