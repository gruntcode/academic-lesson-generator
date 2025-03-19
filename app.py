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
    
    4. REVIEW QUESTIONS:
       - Create 5 review questions with answers
    
    5. QUIZ:
       - Create a 10-question quiz to assess understanding
       - Include an answer key
    
    6. FACILITATOR'S GUIDE FOR HOMESCHOOL EDUCATORS:
       - Provide detailed guidance for parents/teachers in a homeschool setting
       - Include background knowledge that would help teach the topic effectively
       - Suggest teaching strategies specific to this topic
       - Recommend additional resources or activities
       - Include tips for addressing common misconceptions or difficulties
    
    7. WORKSHEET:
       - Create a comprehensive worksheet with activities that complement the lesson
       - Include a mix of question types (multiple choice, short answer, fill-in-the-blank, etc.)
       - Make sure the worksheet is substantial with at least 10 questions or activities
    
    8. REFERENCES:
       - List 5-7 credible sources related to this topic
       - Include books, websites, academic papers, or other educational resources
       - Format each reference properly with author, title, year, and URL if applicable
       - These should be real, verifiable sources that educators could actually use
    
    Format each section with clear headings and organize the content in a logical flow.
    DO NOT use markdown formatting in your response. Instead, use plain text with clear section titles.
    For each section, start with the section name in ALL CAPS followed by a colon, like "LESSON CONTENT:" 
    Separate the worksheet section and facilitator's guide clearly as they should appear on their own pages.
    Ensure the facilitator's guide, worksheet sections, and references are comprehensive and detailed.
    """
    
    # Call the Groq API with increased max tokens
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.2-3b-preview",
        max_tokens=10000  # Increased token limit to ensure complete response
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
    
    story.append(PageBreak())
    
    # Add table of contents
    story.append(Paragraph("TABLE OF CONTENTS", heading_style))
    story.append(Spacer(1, 12))
    
    # Define sections to look for
    sections = [
        "LESSON CONTENT",
        "KEY POINTS",
        "REVIEW QUESTIONS",
        "QUIZ",
        "FACILITATOR'S GUIDE FOR HOMESCHOOL EDUCATORS",
        "WORKSHEET",
        "REFERENCES"
    ]
    
    # Create TOC entries
    toc_data = []
    for i, section in enumerate(sections, 1):
        toc_data.append([f"{i}. {section}", ""])
    
    # Create table for TOC with proper alignment
    toc_table = Table(toc_data, colWidths=[5*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkblue),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(toc_table)
    story.append(PageBreak())
    
    # Process the content
    # Remove markdown formatting
    content = re.sub(r'#+\s+', '', content)  # Remove markdown headers
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Remove bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)  # Remove italic
    content = re.sub(r'`(.*?)`', r'\1', content)  # Remove code
    
    # Split content into sections
    section_pattern = r'([A-Z\s\']+(?:\s+FOR\s+HOMESCHOOL\s+EDUCATORS)?):'
    sections_content = re.split(section_pattern, content)
    
    # Remove empty strings and process sections
    sections_content = [s.strip() for s in sections_content if s.strip()]
    
    current_section = None
    
    for i, section in enumerate(sections_content):
        # Check if this is a section title
        if re.match(r'^[A-Z\s\']+(?:\s+FOR\s+HOMESCHOOL\s+EDUCATORS)?$', section):
            # This is a section title
            current_section = section
            story.append(Paragraph(section, heading_style))
        else:
            # This is section content
            if current_section == "WORKSHEET" or current_section == "FACILITATOR'S GUIDE FOR HOMESCHOOL EDUCATORS" or current_section == "REFERENCES":
                # Add page break before worksheet, facilitator's guide, and references
                story.append(PageBreak())
                story.append(Paragraph(current_section, heading_style))
            
            # Split the content into paragraphs
            paragraphs = section.split('\n\n')
            
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
