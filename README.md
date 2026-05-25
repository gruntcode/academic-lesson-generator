# Academic Lesson Generator

A modern, production-ready web application that generates comprehensive academic lessons in PDF format using Groq's Llama 3.3 70B Versatile LLM. Built with Flask, featuring robust error handling, rate limiting, comprehensive testing, and accessibility features.

![Academic Lesson Generator](./ai_generating_lesson.jpg)

## Features

### Core Functionality
- 🎓 Generate academic lessons on any topic
- 📚 Specify grade level for age-appropriate content
- 🤖 AI-generated comprehensive lesson content using Groq's LLM
- 📝 Includes key points, review questions, and quiz
- 💡 Engaging fun fact section to spark interest
- 📖 References section with credible sources
- 🎯 Lesson description and learning expectations
- 📄 Professional PDF generation with custom styling

### Technical Features
- ⚡ Rate limiting to prevent abuse
- 🔒 Input validation and sanitization
- 🛡️ Comprehensive error handling
- 📊 Structured logging with rotation
- ♿ WCAG accessibility compliance
- 🧪 Comprehensive test suite (90%+ coverage)
- 🎨 Modern dark-themed UI with animations
- 📱 Responsive design for all devices
- ✨ Real-time form validation
- 🔔 User-friendly notifications

## Requirements

- Python 3.9+
- Groq API Key (get one at [console.groq.com](https://console.groq.com))

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd academic-lesson-generator
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (for testing and linting)
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your Groq API key:

```plaintext
GROQ_API_KEY=your_actual_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

## Usage

### Running the Application

For local development:

```bash
python app.py
```

The application starts on `http://127.0.0.1:5000` by default. For production-style runs, use the `wsgi:application` entry point with gunicorn (see [Deployment](#deployment)).

### Using the Web Interface

1. Open your browser and navigate to `http://127.0.0.1:5000`
2. Enter a lesson topic (3-200 characters)
3. Select the appropriate grade level
4. Click "Generate Lesson"
5. Wait for the AI to generate your lesson (typically 30-60 seconds)
6. The PDF will automatically download when ready

### API Endpoints

- `GET /` - Main application page
- `POST /generate-lesson` - Generate a lesson (rate limited)
- `GET /health` - Health check endpoint

## Project Structure

```
academic-lesson-generator/
├── app/
│   ├── __init__.py          # Application factory
│   ├── routes.py            # Route handlers
│   ├── llm_service.py       # LLM integration
│   ├── pdf_generator.py     # PDF generation
│   └── utils.py             # Utility functions
├── tests/
│   ├── conftest.py          # Test configuration
│   ├── test_routes.py       # Route tests
│   ├── test_llm_service.py  # LLM service tests
│   ├── test_pdf_generator.py# PDF generator tests
│   └── test_utils.py        # Utility tests
├── static/
│   ├── css/styles.css       # Stylesheets
│   └── js/script.js         # JavaScript
├── templates/
│   └── index.html           # Main template
├── config.py                # Configuration management
├── app.py                   # Application entry point
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Technology Stack

- **Backend**: Flask 2.3+ (Python web framework)
- **LLM**: Groq's Llama 3.3 70B Versatile
- **PDF Generation**: ReportLab 4.0+
- **Rate Limiting**: Flask-Limiter
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Testing**: pytest with coverage
- **Code Quality**: black, flake8, mypy, isort
- **UI Theme**: Modern Dark Mode with accessibility features

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_routes.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code with black
black .

# Sort imports
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy app/
```

### Project Configuration

Configuration is managed through:
- `config.py` - Application configuration classes
- `.env` - Environment-specific variables (not committed)
- `.env.example` - Template for environment variables

### Rate Limits

Default rate limits (configurable in `.env`):
- 5 requests per minute per IP
- 20 requests per hour per IP

## Deployment

### Run with Docker (recommended)

```bash
cp .env.example .env       # then edit values, especially GROQ_API_KEY + SECRET_KEY
docker compose up --build
```

The container runs gunicorn under a non-root user and exposes port 8000. A
healthcheck on `/health` is built in.

### Run with gunicorn directly

```bash
pip install -r requirements.txt
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export GROQ_API_KEY=...
export FLASK_ENV=production
gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:application
```

### Production checklist

1. `FLASK_ENV=production` — this enables the `SECRET_KEY` and `GROQ_API_KEY` validation in `config.ProductionConfig.validate()` and will refuse to boot if either is missing or set to the development default.
2. Put nginx / a managed load balancer in front for TLS termination.
3. Mount or ship `/app/logs/app.log` to your log aggregator.
4. Tune `RATE_LIMIT_PER_MINUTE` / `RATE_LIMIT_PER_HOUR` for your audience; switch the limiter's `storage_uri` to Redis if you run multiple workers/replicas.

## Troubleshooting

### Common Issues

**Issue**: "GROQ_API_KEY not set" warning
- **Solution**: Create a `.env` file with your API key or set the environment variable

**Issue**: Rate limit exceeded
- **Solution**: Wait a few minutes or adjust rate limits in `.env`

**Issue**: PDF generation fails
- **Solution**: Check logs in `logs/app.log` for detailed error messages

**Issue**: Import errors
- **Solution**: Ensure virtual environment is activated and dependencies are installed

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Format code with black and isort
6. Submit a pull request

## License

MIT

## Acknowledgments

- Powered by [Groq](https://groq.com) for fast LLM inference
- Built with [Flask](https://flask.palletsprojects.com/)
- PDF generation by [ReportLab](https://www.reportlab.com/)
