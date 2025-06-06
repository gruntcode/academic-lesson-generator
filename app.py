import os
from flask import Flask, render_template, request, jsonify, send_file
import groq
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure Groq client
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = groq.Groq(api_key=GROQ_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-lesson', methods=['POST'])
def generate_lesson():
    try:
        # Get form data
        topic = request.form.get('topic')
        grade_level = request.form.get('grade_level')
        
        if not topic or not grade_level:
            return jsonify({"error": "Topic and grade level are required"}), 400
        
        # Generate lesson content using Groq's LLM
        lesson_content = generate_lesson_content(topic, grade_level)
        
        # Generate PDF
        pdf_path = create_pdf(topic, grade_level, lesson_content)
        
        # Return the PDF file for download
        return send_file(pdf_path, as_attachment=True, 
                         download_name=f"{topic.replace(' ', '_')}_lesson.pdf")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_lesson_content(topic, grade_level):
    """Generate lesson content using Groq's LLM."""
    prompt = f"""
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
    
    # Call the Groq API with increased max tokens
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=32000  # Increased to leverage the larger model's capacity
    )
    
    # Extract the generated content
    return chat_completion.choices[0].message.content

def create_pdf(topic, grade_level, content):
    """Create a PDF document with the lesson content."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        pdf_path = temp_file.name
    
    # Set up the document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, 
                           leftMargin=1*inch, rightMargin=1*inch,
                           topMargin=1*inch, bottomMargin=1*inch)
    
    # Create custom styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=24,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_LEFT,
        spaceAfter=12,
        textColor=colors.darkblue,
        spaceBefore=24
    )
    
    subheading_style = ParagraphStyle(
        'Subheading',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=10,
        textColor=colors.darkblue,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=8,
        leading=14
    )
    
    reference_style = ParagraphStyle(
        'Reference',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=6,
        leftIndent=24,
        firstLineIndent=-24,
        leading=14
    )
    
    toc_style = ParagraphStyle(
        'TOC',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        leftIndent=0,
        spaceAfter=6
    )
    
    # Parse the content and build the PDF
    story = []
    
    # Add title page
    story.append(Paragraph(f"Academic Lesson: {topic}", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Grade Level: {grade_level}", subheading_style))
    story.append(Spacer(1, 36))
    
    # Add date
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(f"Date: {today}", normal_style))
    
    # Extract and add lesson description and expectations if available
    description_match = re.search(r'Lesson Description:(.+?)(?=Learning Expectations:|$)', content, re.DOTALL)
    if description_match:
        description = description_match.group(1).strip()
        story.append(Spacer(1, 12))
        story.append(Paragraph("Lesson Description:", subheading_style))
        story.append(Paragraph(description, normal_style))
    
    expectations_match = re.search(r'Learning Expectations:(.+?)(?=LESSON CONTENT:|$)', content, re.DOTALL)
    if expectations_match:
        expectations = expectations_match.group(1).strip()
        story.append(Spacer(1, 12))
        story.append(Paragraph("Learning Expectations:", subheading_style))
        
        # Format expectations as a list if they appear to be in list format
        expectations_lines = expectations.split('\n')
        for line in expectations_lines:
            line = line.strip()
            if line:
                if line.startswith('-') or line.startswith('•'):
                    line = '• ' + line[1:].strip()
                story.append(Paragraph(line, normal_style))
    
    # No page break here to avoid blank page
    
    # Define sections to look for (removed facilitator's guide and worksheet, added fun fact before quiz)
    sections = [
        "LESSON CONTENT",
        "KEY POINTS",
        "REVIEW QUESTIONS",
        "REFERENCES",
        "FUN FACT",
        "QUIZ"
    ]
    
    # No table of contents - removed
    story.append(PageBreak())
    
    # Process the content
    # Remove markdown formatting
    content = re.sub(r'#+\s+', '', content)  # Remove markdown headers
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Remove bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)  # Remove italic
    content = re.sub(r'`(.*?)`', r'\1', content)  # Remove code
    
    # Split content into sections
    section_pattern = r'([A-Z\s\']+):'
    sections_content = re.split(section_pattern, content)
    
    # Remove empty strings and process sections
    sections_content = [s.strip() for s in sections_content if s.strip()]
    
    current_section = None
    
    # Reorder sections to move QUIZ to the end if it exists in the content
    ordered_sections = []
    quiz_section = None
    quiz_content = None
    
    for i in range(0, len(sections_content), 2):
        if i+1 < len(sections_content):
            section_title = sections_content[i]
            section_content = sections_content[i+1] if i+1 < len(sections_content) else ""
            
            # Skip facilitator's guide and worksheet completely
            if "FACILITATOR'S GUIDE" in section_title or section_title == "WORKSHEET":
                continue
                
            # Store quiz for later
            if section_title == "QUIZ":
                quiz_section = section_title
                quiz_content = section_content
            else:
                ordered_sections.append((section_title, section_content))
    
    # Add quiz at the end if it exists
    if quiz_section and quiz_content:
        ordered_sections.append((quiz_section, quiz_content))
    
    # Process sections in the new order
    for section_title, section_content in ordered_sections:
        # This is a section title
        current_section = section_title
        
        # Add page breaks before certain sections
        if current_section == "QUIZ" or current_section == "REFERENCES":
            # Add page break before quiz and references
            story.append(PageBreak())
            
        story.append(Paragraph(current_section, heading_style))
        
        # Split the content into paragraphs
        paragraphs = section_content.split('\n\n')
        
        # Create a special style for fun facts
        if current_section == "FUN FACT":
            # Create a fun fact box with special formatting
            fun_fact_style = ParagraphStyle(
                'FunFact',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_LEFT,
                spaceAfter=8,
                leading=14,
                backColor=colors.lightblue,
                borderColor=colors.blue,
                borderWidth=1,
                borderPadding=10,
                textColor=colors.darkblue
            )
            
            # Add a decorative element before the fun fact
            story.append(Spacer(1, 12))
            story.append(Paragraph("🔍 Did you know?", subheading_style))
            story.append(Spacer(1, 6))
            
            # Process the fun fact content
            lines = section_content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                story.append(Paragraph(line, fun_fact_style))
                
            story.append(Spacer(1, 12))
        # Special formatting for key points, review questions, and quiz
        elif current_section in ["KEY POINTS", "REVIEW QUESTIONS", "QUIZ"]:
            # Process these sections with better formatting
            story.append(Spacer(1, 12))
            
            # Split by lines to better identify list items
            lines = section_content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Format list items properly
                if line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
                    # Remove the marker and add a bullet point
                    clean_line = re.sub(r'^[\-\*\•]\s+', '', line)
                    story.append(Paragraph(f"• {clean_line}", normal_style))
                elif re.match(r'^\d+\.\s', line):  # Numbered items like "1. Question"
                    story.append(Paragraph(line, normal_style))
                else:
                    story.append(Paragraph(line, normal_style))
                    
            # Add spacer after the section
            story.append(Spacer(1, 12))
        else:
            # Process other sections normally
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # Process paragraph by paragraph
                lines = para.split('\n')
                processed_lines = []
                
                for line in lines:
                    line = line.strip()
                    if line:
                        # Check if it's a list item
                        if line.startswith('- ') or line.startswith('* '):
                            line = '• ' + line[2:].strip()
                        processed_lines.append(line)
                
                # Rejoin the processed lines
                processed_para = '\n'.join(processed_lines)
                
                # Special formatting for references
                if current_section == "REFERENCES":
                    # Check if it's a reference item (starts with number or bullet)
                    if re.match(r'^[\d\.\•\-]+', processed_para):
                        # Format as a reference
                        story.append(Paragraph(processed_para, reference_style))
                    else:
                        # It's a normal paragraph in the references section
                        story.append(Paragraph(processed_para, normal_style))
                else:
                    # Check if it's a subheading (all caps followed by text)
                    if re.match(r'^[A-Z\s]{3,}[^a-z]*$', processed_para):
                        story.append(Paragraph(processed_para, subheading_style))
                    else:
                        story.append(Paragraph(processed_para, normal_style))
            
            # Add spacer after each section's content
            story.append(Spacer(1, 12))
    
    # Build the PDF
    doc.build(story)
    
    return pdf_path

if __name__ == '__main__':
    # Check if GROQ_API_KEY is set
    if not GROQ_API_KEY:
        print("Warning: GROQ_API_KEY environment variable is not set.")
        print("Please set it before making API calls to Groq.")
    
    app.run(debug=True)
