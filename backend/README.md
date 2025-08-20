# AI Job Application Assistant

An enterprise-grade, AI-powered job application assistant that helps you find, analyze, and apply to jobs using modern architecture principles and best practices.

## 🏗️ Architecture

This project follows **SOLID principles** and **DRY (Don't Repeat Yourself)** methodology with a clean, modular architecture:

```
src/
├── core/                    # Core interfaces and abstractions
│   ├── job_search.py       # Job search service interface
│   ├── ai_service.py       # AI service interface
│   ├── resume_service.py   # Resume service interface
│   ├── application_service.py # Application service interface
│   └── file_service.py     # File management interface
├── models/                  # Data models and schemas
│   ├── job.py             # Job-related models
│   ├── resume.py          # Resume models
│   ├── application.py     # Application models
│   └── cover_letter.py    # Cover letter models
├── services/               # Service implementations
├── api/                    # FastAPI application and endpoints
│   └── v1/                # API version 1
│       ├── jobs.py        # Job search endpoints
│       ├── resumes.py     # Resume management endpoints
│       ├── applications.py # Application tracking endpoints
│       └── ai.py          # AI service endpoints
├── utils/                  # Utility functions and helpers
│   ├── logger.py          # Centralized logging
│   ├── validators.py      # Input validation
│   ├── text_processing.py # Text analysis utilities
│   └── file_helpers.py    # File handling utilities
└── config.py               # Configuration management
```

### Design Principles

- **SOLID Principles**: Each service has a single responsibility and follows dependency inversion
- **Interface Segregation**: Clean interfaces that are easy to implement and extend
- **Open/Closed**: Easy to add new features without modifying existing code
- **Dependency Injection**: Loose coupling between components
- **Type Safety**: Full type hints throughout the codebase
- **Error Handling**: Comprehensive error handling and logging

## 🚀 Features

- **🔍 Smart Job Search**: Multi-portal job search with AI-powered filtering
- **📝 Resume Optimization**: AI-driven resume analysis and improvement suggestions
- **✉️ Cover Letter Generation**: Personalized cover letters using AI analysis
- **📊 Application Tracking**: Comprehensive application management and status tracking
- **🔒 Enterprise Security**: Secure file handling and input validation
- **📈 Scalable Architecture**: Built for production use with proper separation of concerns

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.10+
- **AI**: Google Gemini AI
- **Job Search**: JobSpy + Custom portal implementations
- **Data Models**: Pydantic with full validation
- **Configuration**: Environment-based configuration with validation
- **Logging**: Centralized logging with rotation and structured output
- **Testing**: pytest with comprehensive test coverage

## 📋 Prerequisites

- Python 3.10 or higher
- Chrome browser (for web scraping)
- Gemini API key

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ai-job-apply
chmod +x start.sh
./start.sh
```

### 2. Configure API Key

The setup script will create a `.env` file. Add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

Get your API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

### 3. Run the Application

```bash
# Using the start script (recommended)
./start.sh

# Or manually
python -m src.main
```

### 4. Access the Interface

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Development Setup

### Install Development Dependencies

```bash
./start.sh --dev
```

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 📚 API Usage

### Job Search

```python
import requests

# Search for jobs
response = requests.post("http://localhost:8000/api/v1/jobs/search", json={
    "keywords": ["python", "developer"],
    "location": "Remote",
    "experience_level": "mid",
    "results_wanted": 20
})

jobs = response.json()
print(f"Found {jobs['total_jobs']} jobs")
```

### Resume Optimization

```python
# Optimize resume for a job
response = requests.post("http://localhost:8000/api/v1/ai/optimize-resume", json={
    "resume_id": "res_123",
    "job_description": "We are looking for a Python developer...",
    "target_role": "Senior Python Developer",
    "company_name": "TechCorp Inc."
})

optimization = response.json()
print(f"Confidence score: {optimization['confidence_score']}")
```

### Cover Letter Generation

```python
# Generate cover letter
response = requests.post("http://localhost:8000/api/v1/ai/generate-cover-letter", json={
    "job_title": "Python Developer",
    "company_name": "TechCorp Inc.",
    "job_description": "We need a developer...",
    "resume_summary": "Experienced Python developer...",
    "tone": "professional"
})

cover_letter = response.json()
print(f"Generated {cover_letter['word_count']} words")
```

## 🔍 Job Portal Support

### Primary (JobSpy)
- **LinkedIn**: Professional networking and job board
- **Indeed**: Global job search engine
- **Glassdoor**: Job reviews and company insights
- **ZipRecruiter**: US/Canada job search
- **Google Jobs**: Google's job search platform

### Fallback (Custom Portals)
- **LinkedIn**: Custom implementation with advanced selectors
- **Indeed**: Custom implementation with rate limiting
- **Glassdoor**: Custom implementation with company data

## 🏭 Production Deployment

### Environment Variables

```env
# Core Configuration
ENVIRONMENT=production
DEBUG=false

# AI Configuration
GEMINI_API_KEY=your_production_api_key
GEMINI_MODEL=gemini-pro

# Security
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=["https://yourdomain.com"]

# Database (if using external database)
DATABASE_URL=postgresql://user:pass@host:port/db

# Logging
LOG_LEVEL=INFO
LOG_ROTATION=1 day
LOG_RETENTION=30 days
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -e .
RUN playwright install chromium

EXPOSE 8000
CMD ["python", "-m", "src.main"]
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_models.py     # Data model tests
│   ├── test_services.py   # Service tests
│   └── test_utils.py      # Utility tests
├── integration/            # Integration tests
│   ├── test_api.py        # API endpoint tests
│   └── test_e2e.py        # End-to-end tests
└── conftest.py            # Test configuration
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=src tests/
```

## 📊 Monitoring and Logging

### Logging Configuration

- **Structured Logging**: JSON-formatted logs for production
- **Log Rotation**: Daily rotation with configurable retention
- **Multiple Handlers**: File and console output
- **Log Levels**: Configurable per environment

### Health Checks

- **Service Health**: `/health` endpoint
- **AI Service Health**: `/api/v1/ai/health`
- **Database Health**: Database connection status
- **External Services**: JobSpy and portal availability

## 🔒 Security Features

- **Input Validation**: Comprehensive validation using Pydantic
- **File Upload Security**: File type and size validation
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Rate Limiting**: Built-in rate limiting for API endpoints
- **Error Handling**: Secure error messages without information leakage

## 🚀 Performance Features

- **Async/Await**: Full async support for I/O operations
- **Connection Pooling**: Database connection pooling
- **Caching**: Built-in caching for frequently accessed data
- **Background Tasks**: Long-running operations in background
- **Resource Management**: Proper cleanup and resource management

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow coding standards**:
   - Use type hints throughout
   - Follow PEP 8 style guidelines
   - Add comprehensive docstrings
   - Write tests for new functionality
4. **Submit pull request**

### Development Guidelines

- **Code Style**: Use Black for formatting
- **Linting**: Use flake8 for code quality
- **Type Checking**: Use mypy for static type checking
- **Testing**: Maintain >90% test coverage
- **Documentation**: Update docs for all changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with FastAPI, Python, and Google Gemini AI
- Follows enterprise software development best practices
- Inspired by modern microservices architecture patterns

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Built with ❤️ following enterprise-grade software development principles**
