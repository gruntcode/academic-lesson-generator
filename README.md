# Academic Lesson Generator

A modern web application that generates comprehensive academic lessons in PDF format using Groq's Llama 3.3 70B Versatile LLM.

## Features

- Generate academic lessons on any topic
- Specify grade level for appropriate content
- AI-generated comprehensive lesson content
- Includes key points, review questions, and quiz
- Engaging fun fact section to spark interest
- References section with credible sources
- Lesson description and learning expectations
- Modern dark-themed UI
- Interactive "Lesson Generating" page with animations
- Automatic PDF download

## Requirements

- Python 3.13+
- Groq API Key

## Installation

Follow these steps to set up the project:

1. Clone this repository or download the source code
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Groq API key as an environment variable:

   ```bash
   # On Windows
   set GROQ_API_KEY=your_api_key_here

   # On macOS/Linux
   export GROQ_API_KEY=your_api_key_here
   ```

   Alternatively, create a `.env` file in the project root with:

   ```plaintext
   GROQ_API_KEY=your_api_key_here
   ```

## Usage

Follow these steps to use the application:

1. Start the Flask application:

   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:

   ```plaintext
   http://127.0.0.1:5000
   ```

3. Fill in the lesson topic and select the grade level
4. Click "Generate Lesson" and wait for the PDF to be generated
5. The PDF will automatically download when ready

## Technology Stack

- **Backend**: Flask (Python)
- **LLM**: Groq's Llama 3.3 70B Versatile
- **PDF Generation**: ReportLab
- **Frontend**: HTML, CSS, JavaScript
- **UI Theme**: Modern Dark Mode

## License

MIT
