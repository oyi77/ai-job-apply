"""Unified application service implementation for the AI Job Application Assistant."""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from src.core.application_service import ApplicationService
from src.models.application import JobApplication, ApplicationUpdateRequest, ApplicationStatus
from src.services.local_file_service import LocalFileService
from src.database.repositories.application_repository import ApplicationRepository
from loguru import logger
from src.core.cache import cache_region


class ApplicationService(ApplicationService):
    """Unified implementation of ApplicationService with database support."""
    
    def __init__(self, file_service: LocalFileService, repository: Optional[ApplicationRepository] = None):
        """Initialize the unified application service."""
        self.logger = logger.bind(module="ApplicationService")
        self.file_service = file_service
        self.repository = repository
        # Fallback to in-memory if no repository provided (for backward compatibility)
        if not self.repository:
            self.applications: Dict[str, JobApplication] = {}
            self.follow_ups: Dict[str, datetime] = {}  # application_id -> follow_up_date
            self._initialize_sample_data()
    
    def _initialize_sample_data(self) -> None:
        """Initialize with some sample data for demonstration."""
        sample_applications = [
            {
                "job_id": "job_1",
                "job_title": "Senior Python Developer",
                "company": "TechCorp Inc.",
                "status": ApplicationStatus.SUBMITTED,
                "applied_date": datetime.utcnow() - timedelta(days=5),
                "notes": "Applied through company website. Good match for skills.",
            },
            {
                "job_id": "job_2", 
                "job_title": "Full Stack Engineer",
                "company": "Innovation Labs",
                "status": ApplicationStatus.UNDER_REVIEW,
                "applied_date": datetime.utcnow() - timedelta(days=3),
                "notes": "Recruiter reached out on LinkedIn. Scheduled for phone screen.",
                "interview_date": datetime.utcnow() + timedelta(days=2),
            },
            {
                "job_id": "job_3",
                "job_title": "Software Architect",
                "company": "StartupXYZ",
                "status": ApplicationStatus.INTERVIEW_SCHEDULED,
                "applied_date": datetime.utcnow() - timedelta(days=10),
                "interview_date": datetime.utcnow() + timedelta(days=1),
                "notes": "Technical interview scheduled. Need to prepare system design questions.",
            }
        ]
        
        for app_data in sample_applications:
            app_id = str(uuid.uuid4())
            application = JobApplication(
                id=app_id,
                **app_data
            )
            self.applications[app_id] = application
        
        self.logger.info("Initialized with sample application data")
    
    async def create_application(self, job_info: Dict[str, Any], resume_path: Optional[str] = None, user_id: Optional[str] = None) -> JobApplication:
        """Create a new job application."""
        try:
            app_id = str(uuid.uuid4())
            
            application = JobApplication(
                id=app_id,
                job_id=job_info.get("job_id", job_info.get("id", str(uuid.uuid4()))),
                job_title=job_info.get("job_title", job_info.get("title", "Unknown Position")),
                company=job_info.get("company", "Unknown Company"),
                location=job_info.get("location", "Unknown Location"),
                status=job_info.get("status", ApplicationStatus.DRAFT),
                applied_date=job_info.get("applied_date"),
                resume_path=resume_path,
                notes=job_info.get("notes", ""),
            )
            
            # Set user_id if provided (for database models)
            if user_id and hasattr(application, 'user_id'):
                application.user_id = user_id
            
            # Use repository if available, otherwise use in-memory storage
            if self.repository:
                application = await self.repository.create(application, user_id=user_id)
            else:
                self.applications[app_id] = application
            
            try:
                # Invalidate stats and list cache
                cache_region.delete_multi([
                    f"application_stats:{user_id}",
                    f"application_list:{user_id}"
                ])
            except Exception as e:
                self.logger.warning(f"Cache invalidation failed: {e}")

            self.logger.info(f"Created application: {application.job_title} at {application.company} (ID: {application.id})")
            return application
            
        except Exception as e:
            self.logger.error(f"Error creating application: {e}", exc_info=True)
            raise
    
    async def get_application(self, application_id: str, user_id: Optional[str] = None) -> Optional[JobApplication]:
        """Get an application by ID, optionally filtered by user."""
        try:
            if self.repository:
                application = await self.repository.get_by_id(application_id, user_id=user_id)
            else:
                application = self.applications.get(application_id)
            
            if application:
                self.logger.debug(f"Retrieved application: {application.job_title} (ID: {application_id})")
            else:
                self.logger.warning(f"Application not found: {application_id}")
            return application
            
        except Exception as e:
            self.logger.error(f"Error getting application {application_id}: {e}", exc_info=True)
            return None
    
    async def get_all_applications(self, user_id: Optional[str] = None) -> List[JobApplication]:
        """Get all applications, optionally filtered by user."""
        try:
            # Check cache
            from dogpile.cache.api import NO_VALUE
            cache_key = f"application_list:{user_id}"
            cached_apps = cache_region.get(cache_key)
            if cached_apps is not NO_VALUE:
                self.logger.debug(f"Cache hit for {cache_key}")
                return cached_apps

            if self.repository:
                applications = await self.repository.get_all(user_id=user_id)
            else:
                applications = list(self.applications.values())
                # Sort by creation date, most recent first
                applications.sort(key=lambda app: app.created_at, reverse=True)
            
            self.logger.debug(f"Retrieved {len(applications)} applications")
            
            # Cache result
            cache_region.set(cache_key, applications)
            
            return applications
            
        except Exception as e:
            self.logger.error(f"Error getting all applications: {e}", exc_info=True)
            return []
    
    async def get_applications_by_status(self, status: ApplicationStatus, user_id: Optional[str] = None) -> List[JobApplication]:
        """Get applications by status, optionally filtered by user."""
        try:
            if self.repository:
                applications = await self.repository.get_by_status(status, user_id=user_id)
            else:
                applications = [
                    app for app in self.applications.values() 
                    if app.status == status
                ]
                # Sort by creation date, most recent first
                applications.sort(key=lambda app: app.created_at, reverse=True)
            
            self.logger.debug(f"Retrieved {len(applications)} applications with status {status}")
            return applications
            
        except Exception as e:
            self.logger.error(f"Error getting applications by status {status}: {e}", exc_info=True)
            return []
    
    async def update_application(self, application_id: str, updates: ApplicationUpdateRequest) -> Optional[JobApplication]:
        """Update application status and information."""
        try:
            application = await self.get_application(application_id)
            if not application:
                self.logger.warning(f"Cannot update, application not found: {application_id}")
                return None
            
            # Update fields if provided
            if updates.status is not None:
                old_status = application.status
                application.status = updates.status
                self.logger.info(f"Updated application status from {old_status} to {updates.status}: {application.job_title}")
                
                # Auto-set applied_date when status changes to SUBMITTED
                if updates.status == ApplicationStatus.SUBMITTED and not application.applied_date:
                    application.applied_date = datetime.utcnow()
            
            if updates.notes is not None:
                application.notes = updates.notes
            
            if updates.follow_up_date is not None:
                application.follow_up_date = updates.follow_up_date
                if not self.repository:
                    self.follow_ups[application_id] = updates.follow_up_date
            
            if updates.interview_date is not None:
                application.interview_date = updates.interview_date
                # Auto-update status if interview is scheduled
                if application.status in [ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW]:
                    application.status = ApplicationStatus.INTERVIEW_SCHEDULED
            
            application.updated_at = datetime.utcnow()
            
            # Save to repository if available
            if self.repository:
                updated_app = await self.repository.update(application_id, updates)
                if updated_app:
                    application = updated_app
            # For in-memory, application is already updated in place

            try:
                user_id = getattr(application, 'user_id', None)
                # Invalidate stats and list cache
                cache_region.delete_multi([
                    f"application_stats:{user_id}",
                    f"application_list:{user_id}"
                ])
            except Exception as e:
                self.logger.warning(f"Cache invalidation failed: {e}")
            
            self.logger.info(f"Updated application: {application.job_title} (ID: {application_id})")
            return application
            
        except Exception as e:
            self.logger.error(f"Error updating application {application_id}: {e}", exc_info=True)
            return None
    
    async def delete_application(self, application_id: str, user_id: Optional[str] = None) -> bool:
        """Delete an application, optionally filtered by user."""
        try:
            application = await self.get_application(application_id, user_id=user_id)
            if not application:
                self.logger.warning(f"Cannot delete, application not found: {application_id}")
                return False
            
            # Delete from repository if available
            if self.repository:
                success = await self.repository.delete(application_id, user_id=user_id)
            else:
                # Remove from storage
                del self.applications[application_id]
                # Remove follow-up if exists
                if application_id in self.follow_ups:
                    del self.follow_ups[application_id]
                success = True
            
            if success:
                try:
                    # Invalidate stats and list cache
                    cache_region.delete_multi([
                        f"application_stats:{user_id}",
                        f"application_list:{user_id}"
                    ])
                except Exception as e:
                    self.logger.warning(f"Cache invalidation failed: {e}")
            
            self.logger.info(f"Deleted application: {application.job_title} (ID: {application_id})")
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting application {application_id}: {e}", exc_info=True)
            return False
    
    async def get_application_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get application statistics, optionally filtered by user."""
        try:
            # Check cache
            from dogpile.cache.api import NO_VALUE
            cache_key = f"application_stats:{user_id}"
            cached_stats = cache_region.get(cache_key)
            if cached_stats is not NO_VALUE:
                self.logger.debug(f"Cache hit for {cache_key}")
                return cached_stats
                
            if self.repository:
                stats = await self.repository.get_statistics(user_id=user_id)
                # Convert status enum keys to string values for consistency
                if "status_breakdown" in stats:
                    status_breakdown = {}
                    for status, count in stats["status_breakdown"].items():
                        status_key = status.value if hasattr(status, 'value') else str(status)
                        status_breakdown[status_key] = count
                    stats["status_breakdown"] = status_breakdown
                    
                # Cache result
                cache_region.set(cache_key, stats)
                return stats
            
            # Fallback to in-memory calculation
            applications = await self.get_all_applications()
            
            # Count by status
            status_breakdown = defaultdict(int)
            for app in applications:
                # Handle both enum and string values
                status_key = app.status.value if hasattr(app.status, 'value') else app.status
                status_breakdown[status_key] += 1
            
            # Ensure all statuses are represented
            for status in ApplicationStatus:
                if status.value not in status_breakdown:
                    status_breakdown[status.value] = 0
            
            # Calculate recent activity
            recent_cutoff = datetime.utcnow() - timedelta(days=30)
            recent_applications = [
                app for app in applications 
                if app.created_at >= recent_cutoff
            ]
            
            # Calculate success metrics
            successful_statuses = [
                ApplicationStatus.OFFER_RECEIVED,
                ApplicationStatus.OFFER_ACCEPTED,
                ApplicationStatus.INTERVIEW_COMPLETED
            ]
            successful_apps = [
                app for app in applications 
                if app.status in successful_statuses
            ]
            
            # Calculate average response time
            response_times = []
            for app in applications:
                if app.applied_date and app.status != ApplicationStatus.DRAFT:
                    # Calculate days since application
                    days_since = (datetime.utcnow() - app.applied_date).days
                    response_times.append(days_since)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            stats = {
                "total_applications": len(applications),
                "status_breakdown": dict(status_breakdown),
                "recent_activity": f"{len(recent_applications)} applications in the last 30 days",
                "success_rate": len(successful_apps) / len(applications) * 100 if applications else 0,
                "average_response_time_days": round(avg_response_time, 1),
                "pending_interviews": len([
                    app for app in applications 
                    if app.status == ApplicationStatus.INTERVIEW_SCHEDULED
                ]),
                "active_applications": len([
                    app for app in applications 
                    if app.status in [
                        ApplicationStatus.SUBMITTED,
                        ApplicationStatus.UNDER_REVIEW,
                        ApplicationStatus.INTERVIEW_SCHEDULED,
                        ApplicationStatus.INTERVIEW_COMPLETED
                    ]
                ])
            }
            
            self.logger.debug("Generated application statistics")
            cache_region.set(cache_key, stats)
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting application stats: {e}", exc_info=True)
            return {
                "total_applications": 0,
                "status_breakdown": {},
                "recent_activity": "0 applications in the last 30 days",
                "error": str(e)
            }
    
    async def schedule_follow_up(self, application_id: str, follow_up_date: str) -> bool:
        """Schedule a follow-up for an application."""
        try:
            application = await self.get_application(application_id)
            if not application:
                self.logger.warning(f"Cannot schedule follow-up, application not found: {application_id}")
                return False
            
            # Parse follow-up date
            try:
                follow_up_datetime = datetime.fromisoformat(follow_up_date.replace('Z', '+00:00'))
            except ValueError:
                # Try parsing without timezone info
                follow_up_datetime = datetime.fromisoformat(follow_up_date)
            
            # Update application
            application.follow_up_date = follow_up_datetime
            application.updated_at = datetime.utcnow()
            
            # Store in follow-ups tracking
            self.follow_ups[application_id] = follow_up_datetime
            
            self.logger.info(f"Scheduled follow-up for {application.job_title} on {follow_up_date}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error scheduling follow-up for {application_id}: {e}", exc_info=True)
            return False
    
    async def get_upcoming_follow_ups(self) -> List[JobApplication]:
        """Get applications with upcoming follow-ups."""
        try:
            if self.repository:
                upcoming_applications = await self.repository.get_upcoming_follow_ups()
            else:
                upcoming_applications = []
                cutoff_date = datetime.utcnow() + timedelta(days=7)  # Next 7 days
                
                for app_id, follow_up_date in self.follow_ups.items():
                    if follow_up_date <= cutoff_date:
                        application = await self.get_application(app_id)
                        if application:
                            upcoming_applications.append(application)
                
                # Sort by follow-up date
                upcoming_applications.sort(key=lambda app: app.follow_up_date or datetime.max)
            
            self.logger.debug(f"Retrieved {len(upcoming_applications)} upcoming follow-ups")
            return upcoming_applications
            
        except Exception as e:
            self.logger.error(f"Error getting upcoming follow-ups: {e}", exc_info=True)
            return []
    
    async def get_applications_by_company(self, company: str, user_id: Optional[str] = None) -> List[JobApplication]:
        """Get all applications for a specific company, optionally filtered by user."""
        try:
            if self.repository:
                applications = await self.repository.get_by_company(company, user_id=user_id)
            else:
                applications = [
                    app for app in self.applications.values()
                    if app.company.lower() == company.lower()
                ]
                applications.sort(key=lambda app: app.created_at, reverse=True)
            
            self.logger.debug(f"Retrieved {len(applications)} applications for {company}")
            return applications
            
        except Exception as e:
            self.logger.error(f"Error getting applications for company {company}: {e}", exc_info=True)
            return []
    
    async def search_applications(self, query: str, user_id: Optional[str] = None) -> List[JobApplication]:
        """Search applications by job title, company, or notes, optionally filtered by user."""
        try:
            if self.repository:
                matching_applications = await self.repository.search(query, user_id=user_id)
            else:
                query_lower = query.lower()
                matching_applications = []
                
                for application in self.applications.values():
                    # Search in job title, company, and notes
                    searchable_text = f"{application.job_title} {application.company} {application.notes or ''}".lower()
                    
                    if query_lower in searchable_text:
                        matching_applications.append(application)
                
                matching_applications.sort(key=lambda app: app.created_at, reverse=True)
            
            self.logger.debug(f"Found {len(matching_applications)} applications matching '{query}'")
            return matching_applications
            
        except Exception as e:
            self.logger.error(f"Error searching applications with query '{query}': {e}", exc_info=True)
            return []
    
    async def get_application_timeline(self, application_id: str) -> List[Dict[str, Any]]:
        """Get timeline of events for an application."""
        try:
            application = await self.get_application(application_id)
            if not application:
                return []
            
            timeline = []
            
            # Created event
            timeline.append({
                "date": application.created_at,
                "event": "Application Created",
                "description": f"Created application for {application.job_title} at {application.company}",
                "status": "draft"
            })
            
            # Applied event
            if application.applied_date:
                timeline.append({
                    "date": application.applied_date,
                    "event": "Application Submitted",
                    "description": f"Submitted application to {application.company}",
                    "status": "submitted"
                })
            
            # Interview scheduled event
            if application.interview_date:
                timeline.append({
                    "date": application.interview_date,
                    "event": "Interview Scheduled",
                    "description": f"Interview scheduled with {application.company}",
                    "status": "interview_scheduled"
                })
            
            # Follow-up event
            if application.follow_up_date:
                timeline.append({
                    "date": application.follow_up_date,
                    "event": "Follow-up Scheduled",
                    "description": f"Follow-up reminder for {application.company}",
                    "status": "follow_up"
                })
            
            # Sort by date
            timeline.sort(key=lambda event: event["date"])
            
            self.logger.debug(f"Generated timeline with {len(timeline)} events for application {application_id}")
            return timeline
            
        except Exception as e:
            self.logger.error(f"Error getting timeline for application {application_id}: {e}", exc_info=True)
            return []

    BULK_OPERATION_LIMIT = 100

    async def bulk_create_applications(self, applications_data: List[Dict[str, Any]], user_id: Optional[str] = None) -> List[JobApplication]:
        """Create multiple job applications."""
        if len(applications_data) > self.BULK_OPERATION_LIMIT:
            raise ValueError(f"Bulk operation limit exceeded: max {self.BULK_OPERATION_LIMIT} items allowed")
            
        try:
            if self.repository:
                # Prepare Application objects
                applications = []
                for app_data in applications_data:
                    app_id = str(uuid.uuid4())
                    application = JobApplication(
                        id=app_id,
                        job_id=app_data.get("job_id", app_data.get("id", str(uuid.uuid4()))),
                        job_title=app_data.get("job_title", app_data.get("title", "Unknown Position")),
                        company=app_data.get("company", "Unknown Company"),
                        location=app_data.get("location", "Unknown Location"),
                        status=app_data.get("status", ApplicationStatus.DRAFT),
                        applied_date=app_data.get("applied_date"),
                        resume_path=app_data.get("resume_path"),
                        notes=app_data.get("notes", ""),
                    )
                    if user_id:
                        application.user_id = user_id
                    applications.append(application)
                
                result = await self.repository.bulk_create(applications, user_id=user_id)
                try:
                    # Invalidate stats and list cache
                    cache_region.delete_multi([
                        f"application_stats:{user_id}",
                        f"application_list:{user_id}"
                    ])
                except Exception as e:
                    self.logger.warning(f"Cache invalidation failed: {e}")
                return result

            else:
                # Fallback to loop
                created_applications = []
                for app_data in applications_data:
                    application = await self.create_application(app_data, user_id=user_id)
                    created_applications.append(application)
                return created_applications
        except Exception as e:
            self.logger.error(f"Error in bulk application creation: {e}", exc_info=True)
            raise

    async def bulk_update_applications(self, application_ids: List[str], updates: ApplicationUpdateRequest, user_id: Optional[str] = None) -> List[JobApplication]:
        """Update multiple job applications."""
        try:
            if self.repository:
                result = await self.repository.bulk_update(application_ids, updates, user_id=user_id)
                try:
                    # Invalidate stats and list cache
                    cache_region.delete_multi([
                        f"application_stats:{user_id}",
                        f"application_list:{user_id}"
                    ])
                except Exception as e:
                    self.logger.warning(f"Cache invalidation failed: {e}")
                return result
            else:
                updated_applications = []
                for app_id in application_ids:
                    # Enforce user check in loop
                    existing = await self.get_application(app_id)
                    if existing and (not user_id or existing.user_id == user_id):
                        application = await self.update_application(app_id, updates)
                        if application:
                            updated_applications.append(application)
                return updated_applications
        except Exception as e:
            self.logger.error(f"Error in bulk application update: {e}", exc_info=True)
            raise

    async def bulk_delete_applications(self, application_ids: List[str], user_id: Optional[str] = None) -> bool:
        """Delete multiple job applications."""
        try:
            if self.repository:
                result = await self.repository.bulk_delete(application_ids, user_id=user_id)
                try:
                    if result:
                        # Invalidate stats and list cache
                        cache_region.delete_multi([
                            f"application_stats:{user_id}",
                            f"application_list:{user_id}"
                        ])
                except Exception as e:
                    self.logger.warning(f"Cache invalidation failed: {e}")
                return result
            else:
                success = True
                for app_id in application_ids:
                    # Enforce user check
                    existing = await self.get_application(app_id)
                    if existing and (not user_id or existing.user_id == user_id):
                        result = await self.delete_application(app_id, user_id=user_id)
                        if not result:
                            success = False
                return success
        except Exception as e:
            self.logger.error(f"Error in bulk application deletion: {e}", exc_info=True)
            return False

    async def export_applications(self, application_ids: Optional[List[str]] = None, format: str = "csv", user_id: Optional[str] = None) -> bytes:
        """Export applications in the specified format."""
        try:
            if application_ids:
                applications = []
                for app_id in application_ids:
                    app = await self.get_application(app_id, user_id=user_id)
                    if app:
                        applications.append(app)
            else:
                applications = await self.get_all_applications(user_id=user_id)

            if format.lower() == "csv":
                import csv
                import io
                output = io.StringIO()
                writer = csv.writer(output)
                # Header
                writer.writerow(["ID", "Job Title", "Company", "Status", "Applied Date", "Notes"])
                for app in applications:
                    writer.writerow([
                        app.id,
                        app.job_title,
                        app.company,
                        app.status,
                        app.applied_date.isoformat() if app.applied_date else "",
                        app.notes or ""
                    ])
                return output.getvalue().encode('utf-8')
            elif format.lower() == "json":
                import json
                apps_dict = [app.dict() for app in applications]
                return json.dumps(apps_dict, default=str).encode('utf-8')
            else:
                raise ValueError(f"Unsupported export format: {format}")
        except Exception as e:
            self.logger.error(f"Error exporting applications: {e}", exc_info=True)
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            applications = await self.get_all_applications()
            follow_ups_count = len(self.follow_ups) if not self.repository else 0
            return {
                "status": "healthy",
                "available": True,
                "application_count": len(applications),
                "follow_ups_scheduled": follow_ups_count,
                "using_database": self.repository is not None
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "available": False,
                "error": str(e)
            }
