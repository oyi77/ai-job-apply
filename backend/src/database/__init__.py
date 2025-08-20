"""Database package for the AI Job Application Assistant."""

from .config import (
    Base, 
    database_config, 
    get_db_session, 
    init_database, 
    close_database
)
from .models import (
    DBResume,
    DBCoverLetter,
    DBJobApplication,
    DBJobSearch,
    DBAIActivity,
    DBFileMetadata,
)

__all__ = [
    # Configuration
    "Base",
    "database_config",
    "get_db_session",
    "init_database",
    "close_database",
    
    # Models
    "DBResume",
    "DBCoverLetter",
    "DBJobApplication",
    "DBJobSearch",
    "DBAIActivity",
    "DBFileMetadata",
]
