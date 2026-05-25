"""Utility functions for the application."""

import os
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

    if len(topic) > current_app.config["MAX_TOPIC_LENGTH"]:
        return False, f"Topic must be less than {current_app.config['MAX_TOPIC_LENGTH']} characters"

    # Reject characters that could break HTML/PDF rendering or template injection.
    if re.search(r"[<>{}]", topic):
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

    if grade_level not in current_app.config["ALLOWED_GRADE_LEVELS"]:
        return False, "Invalid grade level selected"

    return True, None


def sanitize_filename(filename):
    """
    Sanitize a filename to prevent directory traversal and other issues.

    Preserves a single file extension (e.g. ``file.txt`` stays ``file.txt``)
    while still stripping path components and disallowed characters.

    Args:
        filename: The filename to sanitize

    Returns:
        str: Sanitized filename
    """
    filename = os.path.basename(filename)

    # Split into stem + extension so we can keep one dot.
    stem, ext = os.path.splitext(filename)

    stem = re.sub(r"[^\w\s-]", "", stem)
    stem = re.sub(r"[-\s]+", "_", stem).strip("_")

    ext = re.sub(r"[^\w]", "", ext)

    return f"{stem}.{ext}" if ext else stem


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

    if line.startswith(("-", "*", "•")):
        line = line[1:].strip()

    return f"• {line}"
