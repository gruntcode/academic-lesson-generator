"""LLM service for generating lesson content using Groq API."""
import groq
from flask import current_app


class LLMService:
    """Service class for interacting with Groq's LLM."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self.client = None
    
    def initialize(self, api_key):
        """
        Initialize the Groq client.
        
        Args:
            api_key: Groq API key
        """
        if not api_key:
            raise ValueError("GROQ_API_KEY is required")
        self.client = groq.Groq(api_key=api_key)
    
    def generate_lesson_content(self, topic, grade_level):
        """
        Generate comprehensive lesson content using Groq's LLM.
        
        Args:
            topic: The lesson topic
            grade_level: The target grade level
            
        Returns:
            str: Generated lesson content
            
        Raises:
            groq.APIError: If the API request fails
            ValueError: If client is not initialized
        """
        if not self.client:
            raise ValueError("LLM service not initialized")
        
        prompt = self._build_prompt(topic, grade_level)
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=current_app.config['GROQ_MODEL'],
                max_tokens=current_app.config['MAX_TOKENS']
            )
            
            content = chat_completion.choices[0].message.content
            current_app.logger.info(f"Successfully generated lesson for topic: {topic}")
            return content
            
        except groq.APIError as e:
            current_app.logger.error(f"Groq API error: {e}")
            raise
        except Exception as e:
            current_app.logger.error(f"Unexpected error in lesson generation: {e}")
            raise
    
    def _build_prompt(self, topic, grade_level):
        """
        Build the prompt for lesson generation.
        
        Args:
            topic: The lesson topic
            grade_level: The target grade level
            
        Returns:
            str: Formatted prompt
        """
        return f"""
Create a comprehensive academic lesson on "{topic}" for {grade_level} students.

Structure the lesson as follows:

1. TITLE PAGE:
   - Title: {topic}
   - Grade Level: {grade_level}
   - Date: Current date
   - Lesson Description: A brief 2-3 sentence overview of what this lesson covers
   - Learning Expectations: 3-4 clear learning objectives for students

2. LESSON CONTENT:
   - Provide a thorough explanation of the topic
   - Include relevant examples
   - Use language appropriate for {grade_level} students

3. KEY POINTS:
   - List 5-7 key points from the lesson
   - Format each point as a separate bullet point

4. REVIEW QUESTIONS:
   - Create 5 review questions with answers
   - Format each question and answer as separate items

5. REFERENCES:
   - List 5-7 credible sources related to this topic
   - Include books, websites, academic papers, or other educational resources
   - Format each reference properly with author, title, year, and URL if applicable
   - These should be real, verifiable sources that educators could actually use

6. FUN FACT:
   - Include an interesting and engaging fun fact related to the topic
   - This should be something surprising or fascinating that students would enjoy
   - Keep it concise but informative

7. QUIZ:
   - Create a 10-question quiz to assess understanding
   - Include an answer key
   - Format each question and answer as separate items

Format each section with clear headings and organize the content in a logical flow.
DO NOT use markdown formatting in your response. Instead, use plain text with clear section titles.
For each section, start with the section name in ALL CAPS followed by a colon, like "LESSON CONTENT:" 
Ensure the key points, review questions, and quiz are formatted as separate items, not as paragraphs.
Make the fun fact engaging and interesting for students of the specified grade level.
"""


# Global LLM service instance
llm_service = LLMService()
