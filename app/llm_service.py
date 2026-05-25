"""LLM service for generating lesson content using Groq API."""

import groq
from flask import current_app

SYSTEM_PROMPT = (
    "You are an experienced academic lesson designer. "
    "You produce structured, grade-appropriate lessons that teachers can "
    "use directly in the classroom. "
    "Be accurate, age-appropriate, and avoid speculation. "
    "When sources are requested, cite real, verifiable references — never invent them. "
    "Output plain text only. Do not use markdown (`#`, `**`, `*`, backticks, etc.). "
    "Use section titles in ALL CAPS followed by a colon (e.g. 'LESSON CONTENT:'). "
    "Format lists as one item per line beginning with '- '."
)


class LLMService:
    """Service class for interacting with Groq's LLM."""

    def __init__(self):
        self.client = None

    def initialize(self, api_key):
        """Initialize the Groq client."""
        if not api_key:
            raise ValueError("GROQ_API_KEY is required")
        self.client = groq.Groq(api_key=api_key)

    def generate_lesson_content(self, topic, grade_level):
        """Generate comprehensive lesson content using Groq's LLM.

        Raises:
            groq.APIError: If the API request fails.
            ValueError: If client is not initialized.
        """
        if not self.client:
            raise ValueError("LLM service not initialized")

        user_prompt = self._build_user_prompt(topic, grade_level)

        try:
            chat_completion = self.client.chat.completions.create(
                model=current_app.config["GROQ_MODEL"],
                max_tokens=current_app.config["MAX_TOKENS"],
                temperature=current_app.config.get("GROQ_TEMPERATURE", 0.4),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )

            content = chat_completion.choices[0].message.content
            current_app.logger.info(f"Successfully generated lesson for topic: {topic}")
            return content

        except groq.APIError:
            current_app.logger.exception("Groq API error")
            raise
        except Exception:
            current_app.logger.exception("Unexpected error in lesson generation")
            raise

    def _build_user_prompt(self, topic, grade_level):
        """Build the user message describing the lesson to generate."""
        return f"""Create a comprehensive academic lesson on "{topic}" for {grade_level} students.

Use exactly the following sections in this order, each introduced by its ALL CAPS title and a colon:

LESSON OVERVIEW:
  - Title: {topic}
  - Grade Level: {grade_level}
  - Lesson Description: 2-3 sentence overview of what this lesson covers.
  - Learning Expectations: 3-4 clear, measurable objectives (one per line, prefixed with "- ").

LESSON CONTENT:
  - A thorough, grade-appropriate explanation of the topic.
  - Include concrete examples relevant to {grade_level} students.

KEY POINTS:
  - 5-7 bullet points capturing the most important takeaways. One per line, prefixed with "- ".

REVIEW QUESTIONS:
  - 5 open-ended questions with model answers.
  - Format: "Q1: ...", then the next line "A1: ...". Repeat for Q2..Q5.

REFERENCES:
  - 5-7 real, verifiable sources (books, peer-reviewed articles, reputable educational sites).
  - Format each as: Author(s) (Year). Title. Publisher/Journal. URL if applicable.
  - Do NOT fabricate references. If you are unsure of a specific source, omit it.

FUN FACT:
  - One engaging, surprising fact related to the topic, written for {grade_level} students.

QUIZ:
  - 10 questions assessing understanding (mix of multiple choice and short answer).
  - Format: "Q1: ..." then "A1: ..." on the next line. Repeat for Q2..Q10.

Constraints:
  - Plain text only — no markdown formatting.
  - Keep tone academic but accessible for {grade_level}.
  - Do not include any sections beyond those listed above.
"""

    def _build_prompt(self, topic, grade_level):
        """Backwards-compatible wrapper used by the existing test suite."""
        return self._build_user_prompt(topic, grade_level)


llm_service = LLMService()
