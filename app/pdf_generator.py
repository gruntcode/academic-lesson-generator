"""PDF generation service for creating lesson documents."""
import re
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from flask import current_app


# Regex patterns as module-level constants
DESCRIPTION_PATTERN = re.compile(
    r'Lesson Description:(.+?)(?=Learning Expectations:|$)', 
    re.DOTALL
)
EXPECTATIONS_PATTERN = re.compile(
    r'Learning Expectations:(.+?)(?=LESSON CONTENT:|$)', 
    re.DOTALL
)
SECTION_PATTERN = re.compile(r'([A-Z\s\']+):')
MARKDOWN_HEADER_PATTERN = re.compile(r'#+\s+')
MARKDOWN_BOLD_PATTERN = re.compile(r'\*\*(.*?)\*\*')
MARKDOWN_ITALIC_PATTERN = re.compile(r'\*(.*?)\*')
MARKDOWN_CODE_PATTERN = re.compile(r'`(.*?)`')
LIST_ITEM_PATTERN = re.compile(r'^[\-\*\•]\s+')
NUMBERED_ITEM_PATTERN = re.compile(r'^\d+\.\s')
REFERENCE_ITEM_PATTERN = re.compile(r'^[\d\.\•\-]+')
SUBHEADING_PATTERN = re.compile(r'^[A-Z\s]{3,}[^a-z]*$')


class PDFGenerator:
    """Service class for generating PDF documents."""
    
    def __init__(self):
        """Initialize the PDF generator."""
        self.styles = None
    
    def create_pdf(self, topic, grade_level, content):
        """
        Create a PDF document with the lesson content.
        
        Args:
            topic: The lesson topic
            grade_level: The target grade level
            content: The generated lesson content
            
        Returns:
            str: Path to the generated PDF file
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            pdf_path = temp_file.name
        
        current_app.logger.info(f"Creating PDF at: {pdf_path}")
        
        # Set up the document
        doc = SimpleDocTemplate(
            pdf_path, 
            pagesize=letter,
            leftMargin=1*inch, 
            rightMargin=1*inch,
            topMargin=1*inch, 
            bottomMargin=1*inch
        )
        
        # Create styles
        self.styles = self._create_styles()
        
        # Build the PDF content
        story = []
        self._add_title_page(story, topic, grade_level, content)
        story.append(PageBreak())
        self._add_lesson_sections(story, content)
        
        # Build the PDF
        doc.build(story)
        
        current_app.logger.info(f"PDF created successfully: {pdf_path}")
        return pdf_path
    
    def _create_styles(self):
        """
        Create custom paragraph styles for the PDF.
        
        Returns:
            dict: Dictionary of custom styles
        """
        base_styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'Title',
                parent=base_styles['Title'],
                fontSize=24,
                alignment=TA_CENTER,
                spaceAfter=24,
                textColor=colors.darkblue
            ),
            'heading': ParagraphStyle(
                'Heading',
                parent=base_styles['Heading1'],
                fontSize=18,
                alignment=TA_LEFT,
                spaceAfter=12,
                textColor=colors.darkblue,
                spaceBefore=24
            ),
            'subheading': ParagraphStyle(
                'Subheading',
                parent=base_styles['Heading2'],
                fontSize=14,
                alignment=TA_LEFT,
                spaceAfter=10,
                textColor=colors.darkblue,
                spaceBefore=12
            ),
            'normal': ParagraphStyle(
                'Normal',
                parent=base_styles['Normal'],
                fontSize=12,
                alignment=TA_LEFT,
                spaceAfter=8,
                leading=14
            ),
            'reference': ParagraphStyle(
                'Reference',
                parent=base_styles['Normal'],
                fontSize=11,
                alignment=TA_LEFT,
                spaceAfter=6,
                leftIndent=24,
                firstLineIndent=-24,
                leading=14
            ),
            'fun_fact': ParagraphStyle(
                'FunFact',
                parent=base_styles['Normal'],
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
        }
        
        return custom_styles
    
    def _add_title_page(self, story, topic, grade_level, content):
        """
        Add the title page to the PDF.
        
        Args:
            story: The PDF story list
            topic: The lesson topic
            grade_level: The target grade level
            content: The lesson content
        """
        # Add title
        story.append(Paragraph(f"Academic Lesson: {topic}", self.styles['title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Grade Level: {grade_level}", self.styles['subheading']))
        story.append(Spacer(1, 36))
        
        # Add date
        today = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"Date: {today}", self.styles['normal']))
        
        # Extract and add lesson description
        description_match = DESCRIPTION_PATTERN.search(content)
        if description_match:
            description = description_match.group(1).strip()
            story.append(Spacer(1, 12))
            story.append(Paragraph("Lesson Description:", self.styles['subheading']))
            story.append(Paragraph(description, self.styles['normal']))
        
        # Extract and add learning expectations
        expectations_match = EXPECTATIONS_PATTERN.search(content)
        if expectations_match:
            expectations = expectations_match.group(1).strip()
            story.append(Spacer(1, 12))
            story.append(Paragraph("Learning Expectations:", self.styles['subheading']))
            
            expectations_lines = expectations.split('\n')
            for line in expectations_lines:
                line = line.strip()
                if line:
                    if line.startswith(('-', '•')):
                        line = '• ' + line[1:].strip()
                    story.append(Paragraph(line, self.styles['normal']))
    
    def _add_lesson_sections(self, story, content):
        """
        Add lesson sections to the PDF.
        
        Args:
            story: The PDF story list
            content: The lesson content
        """
        # Remove markdown formatting
        content = self._remove_markdown(content)
        
        # Split content into sections
        sections_content = SECTION_PATTERN.split(content)
        sections_content = [s.strip() for s in sections_content if s.strip()]
        
        # Reorder sections to move QUIZ to the end
        ordered_sections = self._reorder_sections(sections_content)
        
        # Process each section
        for section_title, section_content in ordered_sections:
            self._add_section(story, section_title, section_content)
    
    def _remove_markdown(self, content):
        """
        Remove markdown formatting from content.
        
        Args:
            content: The content to clean
            
        Returns:
            str: Content without markdown
        """
        content = MARKDOWN_HEADER_PATTERN.sub('', content)
        content = MARKDOWN_BOLD_PATTERN.sub(r'\1', content)
        content = MARKDOWN_ITALIC_PATTERN.sub(r'\1', content)
        content = MARKDOWN_CODE_PATTERN.sub(r'\1', content)
        return content
    
    def _reorder_sections(self, sections_content):
        """
        Reorder sections to move quiz to the end.
        
        Args:
            sections_content: List of section titles and content
            
        Returns:
            list: Ordered list of (section_title, section_content) tuples
        """
        ordered_sections = []
        quiz_section = None
        quiz_content = None
        
        for i in range(0, len(sections_content), 2):
            if i+1 < len(sections_content):
                section_title = sections_content[i]
                section_content = sections_content[i+1]
                
                # Skip facilitator's guide and worksheet
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
        
        return ordered_sections
    
    def _add_section(self, story, section_title, section_content):
        """
        Add a section to the PDF.
        
        Args:
            story: The PDF story list
            section_title: The section title
            section_content: The section content
        """
        # Add page breaks before certain sections
        if section_title in ["QUIZ", "REFERENCES"]:
            story.append(PageBreak())
        
        story.append(Paragraph(section_title, self.styles['heading']))
        
        # Handle special sections
        if section_title == "FUN FACT":
            self._add_fun_fact_section(story, section_content)
        elif section_title in ["KEY POINTS", "REVIEW QUESTIONS", "QUIZ"]:
            self._add_list_section(story, section_content)
        elif section_title == "REFERENCES":
            self._add_references_section(story, section_content)
        else:
            self._add_normal_section(story, section_content)
    
    def _add_fun_fact_section(self, story, content):
        """Add fun fact section with special formatting."""
        story.append(Spacer(1, 12))
        story.append(Paragraph("🔍 Did you know?", self.styles['subheading']))
        story.append(Spacer(1, 6))
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                story.append(Paragraph(line, self.styles['fun_fact']))
        
        story.append(Spacer(1, 12))
    
    def _add_list_section(self, story, content):
        """Add list-based section (key points, questions, quiz)."""
        story.append(Spacer(1, 12))
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Format list items
            if LIST_ITEM_PATTERN.match(line):
                clean_line = LIST_ITEM_PATTERN.sub('', line)
                story.append(Paragraph(f"• {clean_line}", self.styles['normal']))
            elif NUMBERED_ITEM_PATTERN.match(line):
                story.append(Paragraph(line, self.styles['normal']))
            else:
                story.append(Paragraph(line, self.styles['normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_references_section(self, story, content):
        """Add references section."""
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            lines = para.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if it's a reference item
                if REFERENCE_ITEM_PATTERN.match(line):
                    story.append(Paragraph(line, self.styles['reference']))
                else:
                    story.append(Paragraph(line, self.styles['normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_normal_section(self, story, content):
        """Add normal text section."""
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            lines = para.split('\n')
            processed_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    # Check if it's a list item
                    if line.startswith(('-', '*')):
                        line = '• ' + line[2:].strip()
                    processed_lines.append(line)
            
            # Rejoin the processed lines
            processed_para = '\n'.join(processed_lines)
            
            # Check if it's a subheading
            if SUBHEADING_PATTERN.match(processed_para):
                story.append(Paragraph(processed_para, self.styles['subheading']))
            else:
                story.append(Paragraph(processed_para, self.styles['normal']))
        
        story.append(Spacer(1, 12))


# Global PDF generator instance
pdf_generator = PDFGenerator()
