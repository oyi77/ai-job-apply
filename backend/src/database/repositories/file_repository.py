"""File metadata repository for database operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from pathlib import Path

from src.database.models import DBFileMetadata
from src.utils.logger import get_logger


class FileRepository:
    """Repository for file metadata database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
        self.logger = get_logger(__name__)
    
    async def create(self, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create new file metadata record."""
        try:
            db_file = DBFileMetadata(
                file_path=file_metadata["file_path"],
                file_name=file_metadata["file_name"],
                file_size=file_metadata["file_size"],
                file_type=file_metadata["file_type"],
                mime_type=file_metadata["mime_type"],
                md5_hash=file_metadata["md5_hash"],
                uploaded_at=file_metadata.get("uploaded_at", datetime.utcnow()),
                last_accessed=file_metadata.get("last_accessed", datetime.utcnow()),
                access_count=file_metadata.get("access_count", 0),
                is_active=file_metadata.get("is_active", True)
            )
            
            self.session.add(db_file)
            await self.session.commit()
            await self.session.refresh(db_file)
            
            self.logger.info(f"Created file metadata: {file_metadata['file_name']}")
            return db_file.to_dict()
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating file metadata: {e}", exc_info=True)
            raise
    
    async def get_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by ID."""
        try:
            stmt = select(DBFileMetadata).where(DBFileMetadata.id == file_id)
            result = await self.session.execute(stmt)
            db_file = result.scalar_one_or_none()
            
            if db_file:
                self.logger.debug(f"Retrieved file metadata: {db_file.file_name}")
                return db_file.to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting file metadata {file_id}: {e}", exc_info=True)
            return None
    
    async def get_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by file path."""
        try:
            stmt = select(DBFileMetadata).where(DBFileMetadata.file_path == file_path)
            result = await self.session.execute(stmt)
            db_file = result.scalar_one_or_none()
            
            if db_file:
                self.logger.debug(f"Retrieved file metadata by path: {file_path}")
                return db_file.to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting file metadata by path {file_path}: {e}", exc_info=True)
            return None
    
    async def get_by_hash(self, md5_hash: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by MD5 hash."""
        try:
            stmt = select(DBFileMetadata).where(DBFileMetadata.md5_hash == md5_hash)
            result = await self.session.execute(stmt)
            db_file = result.scalar_one_or_none()
            
            if db_file:
                self.logger.debug(f"Retrieved file metadata by hash: {md5_hash}")
                return db_file.to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting file metadata by hash {md5_hash}: {e}", exc_info=True)
            return None
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all file metadata with optional pagination."""
        try:
            stmt = select(DBFileMetadata)
            
            if active_only:
                stmt = stmt.where(DBFileMetadata.is_active == True)
            
            stmt = stmt.order_by(DBFileMetadata.uploaded_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
            
            result = await self.session.execute(stmt)
            db_files = result.scalars().all()
            
            files = [file.to_dict() for file in db_files]
            self.logger.debug(f"Retrieved {len(files)} file metadata records")
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting all file metadata: {e}", exc_info=True)
            return []
    
    async def get_by_type(self, file_type: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get files by file type."""
        try:
            stmt = select(DBFileMetadata).where(
                and_(
                    func.lower(DBFileMetadata.file_type) == file_type.lower(),
                    DBFileMetadata.is_active == True
                )
            ).order_by(DBFileMetadata.uploaded_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_files = result.scalars().all()
            
            files = [file.to_dict() for file in db_files]
            self.logger.debug(f"Retrieved {len(files)} files with type {file_type}")
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting files by type {file_type}: {e}", exc_info=True)
            return []
    
    async def get_by_size_range(self, min_size: int, max_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get files by size range in bytes."""
        try:
            conditions = [
                DBFileMetadata.file_size >= min_size,
                DBFileMetadata.is_active == True
            ]
            
            if max_size is not None:
                conditions.append(DBFileMetadata.file_size <= max_size)
            
            stmt = select(DBFileMetadata).where(and_(*conditions)).order_by(DBFileMetadata.file_size.desc())
            
            result = await self.session.execute(stmt)
            db_files = result.scalars().all()
            
            files = [file.to_dict() for file in db_files]
            self.logger.debug(f"Retrieved {len(files)} files in size range")
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting files by size range: {e}", exc_info=True)
            return []
    
    async def update_access(self, file_id: str) -> bool:
        """Update file access time and increment access count."""
        try:
            stmt = update(DBFileMetadata).where(
                DBFileMetadata.id == file_id
            ).values(
                last_accessed=datetime.utcnow(),
                access_count=DBFileMetadata.access_count + 1
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                self.logger.debug(f"Updated access for file: {file_id}")
                return True
            
            return False
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating file access {file_id}: {e}", exc_info=True)
            return False
    
    async def update(self, file_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update file metadata."""
        try:
            # Perform update
            stmt = update(DBFileMetadata).where(
                DBFileMetadata.id == file_id
            ).values(**updates)
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                # Return updated file metadata
                updated_file = await self.get_by_id(file_id)
                self.logger.info(f"Updated file metadata: {file_id}")
                return updated_file
            
            self.logger.warning(f"File metadata not found for update: {file_id}")
            return None
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating file metadata {file_id}: {e}", exc_info=True)
            return None
    
    async def soft_delete(self, file_id: str) -> bool:
        """Soft delete file (mark as inactive)."""
        try:
            stmt = update(DBFileMetadata).where(
                DBFileMetadata.id == file_id
            ).values(is_active=False)
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                self.logger.info(f"Soft deleted file: {file_id}")
                return True
            
            self.logger.warning(f"File not found for soft deletion: {file_id}")
            return False
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error soft deleting file {file_id}: {e}", exc_info=True)
            return False
    
    async def hard_delete(self, file_id: str) -> bool:
        """Hard delete file metadata record."""
        try:
            stmt = delete(DBFileMetadata).where(DBFileMetadata.id == file_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                self.logger.info(f"Hard deleted file metadata: {file_id}")
                return True
            
            self.logger.warning(f"File metadata not found for hard deletion: {file_id}")
            return False
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error hard deleting file metadata {file_id}: {e}", exc_info=True)
            return False
    
    async def search(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search files by name, path, or type."""
        try:
            search_term = f"%{query.lower()}%"
            
            stmt = select(DBFileMetadata).where(
                and_(
                    or_(
                        func.lower(DBFileMetadata.file_name).like(search_term),
                        func.lower(DBFileMetadata.file_path).like(search_term),
                        func.lower(DBFileMetadata.file_type).like(search_term),
                        func.lower(DBFileMetadata.mime_type).like(search_term)
                    ),
                    DBFileMetadata.is_active == True
                )
            ).order_by(DBFileMetadata.uploaded_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_files = result.scalars().all()
            
            files = [file.to_dict() for file in db_files]
            self.logger.debug(f"Found {len(files)} files matching '{query}'")
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error searching files with query '{query}': {e}", exc_info=True)
            return []
    
    async def get_recent(self, days: int = 30, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recently uploaded files."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = select(DBFileMetadata).where(
                and_(
                    DBFileMetadata.uploaded_at >= cutoff_date,
                    DBFileMetadata.is_active == True
                )
            ).order_by(DBFileMetadata.uploaded_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_files = result.scalars().all()
            
            files = [file.to_dict() for file in db_files]
            self.logger.debug(f"Retrieved {len(files)} files from last {days} days")
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting recent files: {e}", exc_info=True)
            return []
    
    async def get_unused_files(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get files that haven't been accessed in the specified number of days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = select(DBFileMetadata).where(
                and_(
                    DBFileMetadata.last_accessed < cutoff_date,
                    DBFileMetadata.is_active == True
                )
            ).order_by(DBFileMetadata.last_accessed.asc())
            
            result = await self.session.execute(stmt)
            db_files = result.scalars().all()
            
            files = [file.to_dict() for file in db_files]
            self.logger.debug(f"Retrieved {len(files)} unused files (>{days} days)")
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting unused files: {e}", exc_info=True)
            return []
    
    async def find_duplicates(self) -> List[Dict[str, Any]]:
        """Find duplicate files based on MD5 hash."""
        try:
            stmt = select(
                DBFileMetadata.md5_hash,
                func.count(DBFileMetadata.id).label('count')
            ).where(
                DBFileMetadata.is_active == True
            ).group_by(
                DBFileMetadata.md5_hash
            ).having(func.count(DBFileMetadata.id) > 1)
            
            result = await self.session.execute(stmt)
            duplicates = []
            
            for md5_hash, count in result.all():
                # Get the actual files for this hash
                detail_stmt = select(DBFileMetadata).where(
                    and_(
                        DBFileMetadata.md5_hash == md5_hash,
                        DBFileMetadata.is_active == True
                    )
                ).order_by(DBFileMetadata.uploaded_at.desc())
                
                detail_result = await self.session.execute(detail_stmt)
                files = detail_result.scalars().all()
                
                duplicates.append({
                    "md5_hash": md5_hash,
                    "count": count,
                    "files": [file.to_dict() for file in files]
                })
            
            self.logger.debug(f"Found {len(duplicates)} duplicate file groups")
            return duplicates
            
        except Exception as e:
            self.logger.error(f"Error finding duplicate files: {e}", exc_info=True)
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get file storage statistics."""
        try:
            # Get total count and size
            total_stmt = select(
                func.count(DBFileMetadata.id),
                func.sum(DBFileMetadata.file_size)
            ).where(DBFileMetadata.is_active == True)
            
            total_result = await self.session.execute(total_stmt)
            total_files, total_size = total_result.first() or (0, 0)
            
            # Get file type breakdown
            type_stmt = select(
                DBFileMetadata.file_type,
                func.count(DBFileMetadata.id),
                func.sum(DBFileMetadata.file_size)
            ).where(
                DBFileMetadata.is_active == True
            ).group_by(DBFileMetadata.file_type)
            
            type_result = await self.session.execute(type_stmt)
            type_breakdown = {}
            for file_type, count, size in type_result.all():
                type_breakdown[file_type] = {
                    "count": count,
                    "total_size": size or 0
                }
            
            # Get average file size
            avg_size_stmt = select(func.avg(DBFileMetadata.file_size)).where(DBFileMetadata.is_active == True)
            avg_size_result = await self.session.execute(avg_size_stmt)
            avg_file_size = avg_size_result.scalar() or 0
            
            # Get recent activity (last 30 days)
            recent_cutoff = datetime.utcnow() - timedelta(days=30)
            recent_stmt = select(func.count(DBFileMetadata.id)).where(
                and_(
                    DBFileMetadata.uploaded_at >= recent_cutoff,
                    DBFileMetadata.is_active == True
                )
            )
            recent_result = await self.session.execute(recent_stmt)
            recent_files = recent_result.scalar()
            
            # Get access statistics
            access_stmt = select(
                func.avg(DBFileMetadata.access_count),
                func.max(DBFileMetadata.access_count)
            ).where(DBFileMetadata.is_active == True)
            
            access_result = await self.session.execute(access_stmt)
            avg_access, max_access = access_result.first() or (0, 0)
            
            stats = {
                "total_files": total_files,
                "total_size_bytes": total_size or 0,
                "total_size_mb": round((total_size or 0) / (1024 * 1024), 2),
                "average_file_size_bytes": round(avg_file_size, 2),
                "file_type_breakdown": type_breakdown,
                "recent_activity": f"{recent_files} files in the last 30 days",
                "access_statistics": {
                    "average_access_count": round(avg_access or 0, 1),
                    "max_access_count": max_access or 0
                }
            }
            
            self.logger.debug("Generated file storage statistics from database")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting file storage stats: {e}", exc_info=True)
            return {
                "total_files": 0,
                "total_size_bytes": 0,
                "recent_activity": "0 files in the last 30 days",
                "error": str(e)
            }
    
    async def cleanup_orphaned_metadata(self) -> int:
        """Remove metadata for files that no longer exist on disk."""
        try:
            # Get all active file records
            stmt = select(DBFileMetadata).where(DBFileMetadata.is_active == True)
            result = await self.session.execute(stmt)
            db_files = result.scalars().all()
            
            orphaned_count = 0
            
            for db_file in db_files:
                # Check if file exists on disk
                if not Path(db_file.file_path).exists():
                    # Mark as inactive
                    await self.soft_delete(db_file.id)
                    orphaned_count += 1
                    self.logger.debug(f"Marked orphaned file as inactive: {db_file.file_path}")
            
            self.logger.info(f"Cleaned up {orphaned_count} orphaned file metadata records")
            return orphaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up orphaned metadata: {e}", exc_info=True)
            return 0
