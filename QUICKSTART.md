# Quick Start Guide

Get the Academic Lesson Generator up and running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- A Groq API key ([Get one free here](https://console.groq.com))

## Installation Steps

### 1. Set up Python Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_actual_api_key_here
```

Or set it directly:
```bash
export GROQ_API_KEY=your_actual_api_key_here
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open in Browser

Navigate to: **http://127.0.0.1:5000**

## First Lesson

1. Enter a topic (e.g., "Photosynthesis")
2. Select grade level (e.g., "Middle School (Grades 6-8)")
3. Click "Generate Lesson"
4. Wait 30-60 seconds
5. Your PDF will download automatically!

## Troubleshooting

**Can't start the app?**
- Make sure virtual environment is activated
- Check that all dependencies are installed: `pip list`

**API key error?**
- Verify your `.env` file exists and contains `GROQ_API_KEY=...`
- Or set it in your shell: `export GROQ_API_KEY=your_key`

**Rate limit error?**
- Wait a few minutes between requests
- Default limit: 5 requests per minute

## Development Mode

Want to contribute or modify the code?

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .

# Check code quality
flake8 .
```

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Check [CHANGES.md](CHANGES.md) to see what's new
- Explore the `app/` directory to understand the code structure
- Run tests to see how everything works: `pytest -v`

## Need Help?

- Check logs in `logs/app.log` for errors
- Review the [Troubleshooting section](README.md#troubleshooting) in README
- Ensure you're using Python 3.9+

Enjoy creating amazing lessons! 🎓
