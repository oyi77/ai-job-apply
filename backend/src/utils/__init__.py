"""Utility functions and helpers for the AI Job Application Assistant."""

from src.utils.logger import get_logger
from src.utils.validators import validate_email, validate_url, validate_file_type
from src.utils.cache import SimpleCache, get_cache
from src.utils.text_processing import clean_text, extract_skills, calculate_similarity
from src.utils.file_helpers import get_file_extension, get_file_size, is_valid_file

__all__ = [
    "get_logger",
    "validate_email",
    "SimpleCache",
    "get_cache",
    "validate_url", 
    "validate_file_type",
    "clean_text",
    "extract_skills",
    "calculate_similarity",
    "get_file_extension",
    "get_file_size",
    "is_valid_file",
]
