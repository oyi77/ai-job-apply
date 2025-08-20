"""Text processing utilities for the AI Job Application Assistant."""

import re
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:]', '', text)
    
    # Normalize line breaks
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_skills(text: str, skill_keywords: Optional[List[str]] = None) -> List[str]:
    """
    Extract skills from text content.
    
    Args:
        text: Text to analyze
        skill_keywords: Optional list of skill keywords to look for
        
    Returns:
        List of extracted skills
    """
    if not text:
        return []
    
    # Default skill keywords if none provided
    if skill_keywords is None:
        skill_keywords = [
            # Programming languages
            "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Swift",
            "TypeScript", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Shell", "Bash",
            
            # Frameworks and libraries
            "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "Spring",
            "Laravel", "ASP.NET", "FastAPI", "TensorFlow", "PyTorch", "Scikit-learn",
            
            # Databases
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", "SQL Server",
            
            # Cloud platforms
            "AWS", "Azure", "Google Cloud", "Heroku", "DigitalOcean", "Vercel",
            
            # Tools and technologies
            "Git", "Docker", "Kubernetes", "Jenkins", "CI/CD", "REST API", "GraphQL",
            "Microservices", "Agile", "Scrum", "DevOps", "Linux", "Unix"
        ]
    
    # Clean text
    cleaned_text = clean_text(text)
    
    # Find skills in text (case-insensitive)
    found_skills = []
    for skill in skill_keywords:
        if re.search(rf'\b{re.escape(skill)}\b', cleaned_text, re.IGNORECASE):
            found_skills.append(skill)
    
    return found_skills


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two text strings.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Clean both texts
    clean_text1 = clean_text(text1)
    clean_text2 = clean_text(text2)
    
    # Use SequenceMatcher for similarity calculation
    similarity = SequenceMatcher(None, clean_text1, clean_text2).ratio()
    
    return round(similarity, 3)


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract key terms from text.
    
    Args:
        text: Text to analyze
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    # Clean text
    cleaned_text = clean_text(text)
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
        'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Split into words and filter
    words = re.findall(r'\b\w+\b', cleaned_text.lower())
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count word frequency
    word_count = {}
    for word in filtered_words:
        word_count[word] = word_count.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, count in sorted_words[:max_keywords]]
    
    return keywords


def normalize_job_title(title: str) -> str:
    """
    Normalize job title for consistent comparison.
    
    Args:
        title: Raw job title
        
    Returns:
        Normalized job title
    """
    if not title:
        return ""
    
    # Convert to lowercase
    normalized = title.lower()
    
    # Remove common prefixes/suffixes
    normalized = re.sub(r'\b(senior|junior|lead|principal|staff|sr|jr)\b', '', normalized)
    normalized = re.sub(r'\b(developer|engineer|programmer|coder|architect|specialist|analyst)\b', '', normalized)
    
    # Clean up extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized


def extract_company_info(text: str) -> Dict[str, str]:
    """
    Extract company information from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with extracted company information
    """
    if not text:
        return {}
    
    # Clean text
    cleaned_text = clean_text(text)
    
    # Extract company name (look for patterns like "at Company Name" or "Company Name is")
    company_patterns = [
        r'\bat\s+([A-Z][a-zA-Z\s&]+?)(?:\s+is|\s+has|\s+offers|\s+provides)',
        r'([A-Z][a-zA-Z\s&]+?)\s+is\s+a',
        r'([A-Z][a-zA-Z\s&]+?)\s+offers',
        r'([A-Z][a-zA-Z\s&]+?)\s+provides'
    ]
    
    company_name = ""
    for pattern in company_patterns:
        match = re.search(pattern, cleaned_text)
        if match:
            company_name = match.group(1).strip()
            break
    
    # Extract location (look for city, state patterns)
    location_pattern = r'([A-Z][a-zA-Z\s]+),\s*([A-Z]{2})'
    location_match = re.search(location_pattern, cleaned_text)
    
    location = ""
    if location_match:
        location = f"{location_match.group(1).strip()}, {location_match.group(2)}"
    
    return {
        "company_name": company_name,
        "location": location
    }


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count words in
        
    Returns:
        Word count
    """
    if not text:
        return 0
    
    # Clean text and split into words
    cleaned_text = clean_text(text)
    words = re.findall(r'\b\w+\b', cleaned_text)
    
    return len(words)


def estimate_reading_time(text: str, words_per_minute: int = 200) -> float:
    """
    Estimate reading time for text.
    
    Args:
        text: Text to estimate reading time for
        words_per_minute: Average reading speed
        
    Returns:
        Estimated reading time in minutes
    """
    word_count = count_words(text)
    reading_time = word_count / words_per_minute
    
    return round(reading_time, 1)
