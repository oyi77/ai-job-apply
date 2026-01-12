"""Database package for the AI Job Application Assistant."""

from src.database.config import (
    Base, 
    database_config, 
    get_db_session, 
    init_database, 
    close_database
)
from src.database.models import (
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
