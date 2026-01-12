"""
Input sanitization utilities.
"""

import html
import re
from typing import Any, Dict, List, Union
from bleach import clean

# Allowed tags for "rich text" fields (e.g. cover letter body)
ALLOWED_TAGS = ['b', 'i', 'u', 'p', 'br', 'ul', 'ol', 'li', 'strong', 'em']
ALLOWED_ATTRIBUTES = {}  # No attributes allowed (no style, no onclick, etc.)


def sanitize_html(content: str) -> str:
    """
    Sanitize HTML content to prevent XSS.
    
    Args:
        content: Raw string content
        
    Returns:
        Sanitized string
    """
    if not content:
        return ""
        
    return clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


def sanitize_text(content: str) -> str:
    """
    Strict sanitization for plain text fields (names, titles).
    Removes all HTML tags.
    
    Args:
        content: Raw string
        
    Returns:
        Plain text string
    """
    if not content:
        return ""
        
    # Unescape allowed entities then strip all tags
    return html.escape(content, quote=True)


def sanitize_input(data: Union[Dict, List, str, int, float, None]) -> Any:
    """
    Recursively sanitize input data structure.
    
    Args:
        data: Input data (dict, list, or primitive)
        
    Returns:
        Sanitized data
    """
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(i) for i in data]
    elif isinstance(data, str):
        # Determine if it looks like HTML or simple text
        # For safety, default single strings to text sanitization
        # Specific fields needing HTML should call sanitize_html directly
        return sanitize_text(data)
    else:
        return data
