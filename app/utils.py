"""Utility functions for the application."""
import re
from flask import current_app


def validate_topic(topic):
    """
    Validate lesson topic input.
    
    Args:
        topic: The topic string to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not topic:
        return False, "Topic is required"
    
    topic = topic.strip()
    
    if len(topic) < 3:
        return False, "Topic must be at least 3 characters long"
    
    if len(topic) > current_app.config['MAX_TOPIC_LENGTH']:
        return False, f"Topic must be less than {current_app.config['MAX_TOPIC_LENGTH']} characters"
    
    # Check for potentially malicious content
    if re.search(r'[<>{}]', topic):
        return False, "Topic contains invalid characters"
    
    return True, None


def validate_grade_level(grade_level):
    """
    Validate grade level input.
    
    Args:
        grade_level: The grade level string to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not grade_level:
        return False, "Grade level is required"
    
    grade_level = grade_level.strip()
    
    if grade_level not in current_app.config['ALLOWED_GRADE_LEVELS']:
        return False, "Invalid grade level selected"
    
    return True, None


def sanitize_filename(filename):
    """
    Sanitize a filename to prevent directory traversal and other issues.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Replace spaces and special characters
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '_', filename)
    
    return filename


def format_list_item(line):
    """
    Format a line as a list item with proper bullet point.
    
    Args:
        line: The line to format
        
    Returns:
        str: Formatted line with bullet point
    """
    line = line.strip()
    
    if not line:
        return line
    
    # Remove existing markers
    if line.startswith(('-', '*', '•')):
        line = line[1:].strip()
    
    # Add bullet point
    return f'• {line}'


import os
