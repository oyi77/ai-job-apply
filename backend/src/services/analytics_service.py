"""
Advanced Analytics Service for Job Application Tracking

Provides comprehensive analytics including:
- Application success rates
- Response time analysis
- Interview performance tracking
- Trend analysis
- Skills gap analysis (AI-powered)
- Company analysis
"""

from typing import Dict, List, Any, Optional, Sequence
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from loguru import logger

from src.models.application import JobApplication, ApplicationStatus
from src.database.repositories.application_repository import ApplicationRepository


class AnalyticsService:
    """Service for advanced analytics and reporting."""

    def __init__(
        self,
        repository: Optional[ApplicationRepository] = None,
        ai_service: Optional[Any] = None,
    ):
        """Initialize analytics service.

        Args:
            repository: Application repository for data access
            ai_service: AI service for intelligent analysis (optional)
        """
        self.repository = repository
        self.ai_service = ai_service
        self.logger = logger.bind(module="AnalyticsService")

    def _filter_by_date(
        self,
        applications: Sequence[JobApplication],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> List[JobApplication]:
        if not start_date and not end_date:
            return list(applications)
        return [
            app
            for app in applications
            if (not start_date or app.created_at >= start_date)
            and (not end_date or app.created_at <= end_date)
        ]

    def _require_applications_or_repository(
        self, applications: Optional[Sequence[JobApplication]]
    ) -> None:
        if applications is None and self.repository is None:
            raise RuntimeError(
                "AnalyticsService requires either a repository or a pre-fetched "
                "applications list"
            )

    async def get_application_success_rate(
        self,
        user_id: str,
        applications: Optional[Sequence[JobApplication]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Calculate application success rate metrics.

        Args:
            user_id: User ID to analyze
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Dictionary with success rate metrics
        """
        try:
            self._require_applications_or_repository(applications)
            if applications is None:
                assert self.repository is not None
                applications = await self.repository.get_all(user_id=user_id)

            applications = self._filter_by_date(applications, start_date, end_date)

            total = len(applications)
            if total == 0:
                return {"total_applications": 0, "success_rate": 0.0, "breakdown": {}}

            # Count by status
            status_counts = defaultdict(int)
            for app in applications:
                status_counts[app.status] += 1

            # Calculate success metrics
            successful = status_counts.get(
                ApplicationStatus.OFFER_RECEIVED, 0
            ) + status_counts.get(ApplicationStatus.OFFER_ACCEPTED, 0)

            interviews = (
                status_counts.get(ApplicationStatus.INTERVIEW_SCHEDULED, 0)
                + status_counts.get(ApplicationStatus.INTERVIEW_COMPLETED, 0)
                + successful
            )

            rejected = status_counts.get(ApplicationStatus.REJECTED, 0)

            return {
                "total_applications": total,
                "successful_applications": successful,
                "success_rate": round((successful / total) * 100, 2),
                "interview_rate": round((interviews / total) * 100, 2),
                "rejection_rate": round((rejected / total) * 100, 2),
                "breakdown": {
                    "draft": status_counts.get(ApplicationStatus.DRAFT, 0),
                    "submitted": status_counts.get(ApplicationStatus.SUBMITTED, 0),
                    "under_review": status_counts.get(
                        ApplicationStatus.UNDER_REVIEW, 0
                    ),
                    "interview_scheduled": status_counts.get(
                        ApplicationStatus.INTERVIEW_SCHEDULED, 0
                    ),
                    "interview_completed": status_counts.get(
                        ApplicationStatus.INTERVIEW_COMPLETED, 0
                    ),
                    "offer_received": status_counts.get(
                        ApplicationStatus.OFFER_RECEIVED, 0
                    ),
                    "offer_accepted": status_counts.get(
                        ApplicationStatus.OFFER_ACCEPTED, 0
                    ),
                    "rejected": rejected,
                    "withdrawn": status_counts.get(ApplicationStatus.WITHDRAWN, 0),
                },
            }

        except Exception as e:
            self.logger.error(f"Error calculating success rate: {e}", exc_info=True)
            raise

    async def get_response_time_analysis(
        self,
        user_id: str,
        applications: Optional[Sequence[JobApplication]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Analyze response times from companies.

        Returns average time to hear back, time to interview, etc.
        """
        try:
            self._require_applications_or_repository(applications)
            if applications is None:
                assert self.repository is not None
                applications = await self.repository.get_all(user_id=user_id)

            applications = self._filter_by_date(applications, start_date, end_date)

            response_times = []
            interview_times = []

            for app in applications:
                if app.updated_at and app.created_at:
                    # Time to any response
                    if app.status != ApplicationStatus.SUBMITTED:
                        days = (app.updated_at - app.created_at).days
                        response_times.append(days)

                    # Time to interview
                    if app.status in [
                        ApplicationStatus.INTERVIEW_SCHEDULED,
                        ApplicationStatus.INTERVIEW_COMPLETED,
                        ApplicationStatus.OFFER_RECEIVED,
                        ApplicationStatus.OFFER_ACCEPTED,
                    ]:
                        days = (app.updated_at - app.created_at).days
                        interview_times.append(days)

            return {
                "avg_response_time_days": round(
                    sum(response_times) / len(response_times), 1
                )
                if response_times
                else 0,
                "avg_interview_time_days": round(
                    sum(interview_times) / len(interview_times), 1
                )
                if interview_times
                else 0,
                "fastest_response_days": min(response_times) if response_times else 0,
                "slowest_response_days": max(response_times) if response_times else 0,
                "total_responses": len(response_times),
                "total_interviews": len(interview_times),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing response times: {e}", exc_info=True)
            raise

    async def get_interview_performance(
        self,
        user_id: str,
        applications: Optional[Sequence[JobApplication]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Track interview performance metrics.
        """
        try:
            self._require_applications_or_repository(applications)
            if applications is None:
                assert self.repository is not None
                applications = await self.repository.get_all(user_id=user_id)

            applications = self._filter_by_date(applications, start_date, end_date)

            total_interviews = 0
            offers_after_interview = 0
            rejections_after_interview = 0

            for app in applications:
                if app.status in [
                    ApplicationStatus.INTERVIEW_SCHEDULED,
                    ApplicationStatus.INTERVIEW_COMPLETED,
                    ApplicationStatus.OFFER_RECEIVED,
                    ApplicationStatus.OFFER_ACCEPTED,
                ]:
                    total_interviews += 1

                    if app.status in [
                        ApplicationStatus.OFFER_RECEIVED,
                        ApplicationStatus.OFFER_ACCEPTED,
                    ]:
                        offers_after_interview += 1
                    elif app.status == ApplicationStatus.REJECTED:
                        rejections_after_interview += 1

            interview_to_offer_rate = (
                round((offers_after_interview / total_interviews) * 100, 2)
                if total_interviews > 0
                else 0
            )

            return {
                "total_interviews": total_interviews,
                "offers_received": offers_after_interview,
                "rejections_after_interview": rejections_after_interview,
                "interview_to_offer_rate": interview_to_offer_rate,
                "pending_interviews": sum(
                    1
                    for app in applications
                    if app.status
                    in [
                        ApplicationStatus.INTERVIEW_SCHEDULED,
                        ApplicationStatus.INTERVIEW_COMPLETED,
                    ]
                ),
            }

        except Exception as e:
            self.logger.error(
                f"Error analyzing interview performance: {e}", exc_info=True
            )
            raise

    async def get_trend_analysis(
        self,
        user_id: str,
        days: int = 30,
        applications: Optional[Sequence[JobApplication]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze trends over time (time series data).

        Args:
            user_id: User ID
            days: Number of days to analyze
        """
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)

            self._require_applications_or_repository(applications)
            if applications is None:
                assert self.repository is not None
                applications = await self.repository.get_all(user_id=user_id)

            applications = [app for app in applications if app.created_at >= start_date]

            # Group by week
            weekly_data = defaultdict(
                lambda: {"applications": 0, "interviews": 0, "offers": 0}
            )

            for app in applications:
                week_start = app.created_at - timedelta(days=app.created_at.weekday())
                week_key = week_start.strftime("%Y-%m-%d")

                weekly_data[week_key]["applications"] += 1

                if app.status in [
                    ApplicationStatus.INTERVIEW_SCHEDULED,
                    ApplicationStatus.INTERVIEW_COMPLETED,
                    ApplicationStatus.OFFER_RECEIVED,
                    ApplicationStatus.OFFER_ACCEPTED,
                ]:
                    weekly_data[week_key]["interviews"] += 1

                if app.status in [
                    ApplicationStatus.OFFER_RECEIVED,
                    ApplicationStatus.OFFER_ACCEPTED,
                ]:
                    weekly_data[week_key]["offers"] += 1

            # Convert to sorted list
            trends = [
                {"week": week, **data} for week, data in sorted(weekly_data.items())
            ]

            return {
                "period_days": days,
                "total_applications": len(applications),
                "weekly_trends": trends,
                "avg_applications_per_week": round(len(applications) / (days / 7), 1)
                if days > 0
                else 0,
            }

        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}", exc_info=True)
            raise

    async def get_skills_gap_analysis(
        self,
        user_id: str,
        applications: Optional[Sequence[JobApplication]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze skills gaps based on job requirements vs user skills using AI.

        Uses Gemini AI to intelligently extract skills from job descriptions
        and provide personalized recommendations.
        """
        try:
            self._require_applications_or_repository(applications)
            if applications is None:
                assert self.repository is not None
                applications = await self.repository.get_all(user_id=user_id)

            if not applications:
                return {
                    "top_required_skills": [],
                    "total_applications_analyzed": 0,
                    "ai_powered": False,
                    "recommendations": [],
                }

            # Use AI service if available for intelligent skills extraction
            if self.ai_service and await self.ai_service.is_available():
                self.logger.info("Using AI-powered skills gap analysis")
                return await self._ai_powered_skills_analysis(applications, user_id)
            else:
                self.logger.info("AI service not available, using fallback analysis")
                return await self._fallback_skills_analysis(applications)

        except Exception as e:
            self.logger.error(f"Error analyzing skills gap: {e}", exc_info=True)
            raise

    async def _ai_powered_skills_analysis(
        self, applications: Sequence[JobApplication], user_id: str
    ) -> Dict[str, Any]:
        """AI-powered skills gap analysis using Gemini."""
        try:
            # Aggregate job descriptions
            job_descriptions = []
            for app in applications:
                job_description = getattr(app, "job_description", None) or app.notes
                if job_description:
                    job_descriptions.append(
                        {
                            "company": app.company,
                            "title": app.job_title,
                            "description": str(job_description)[:500],  # Limit length
                        }
                    )

            if not job_descriptions:
                return await self._fallback_skills_analysis(applications)

            # Use AI service to analyze skills gap
            assert self.ai_service is not None
            analysis = await self.ai_service.analyze_skills_gap(job_descriptions)

            # Add total applications analyzed to the response
            analysis["total_applications_analyzed"] = len(applications)

            return analysis

        except Exception as e:
            self.logger.error(f"Error in AI-powered analysis: {e}", exc_info=True)
            return await self._fallback_skills_analysis(applications)

    async def _fallback_skills_analysis(
        self, applications: Sequence[JobApplication]
    ) -> Dict[str, Any]:
        """Fallback skills analysis using keyword matching."""
        # Extract required skills from job descriptions
        all_required_skills = []
        for app in applications:
            job_description = getattr(app, "job_description", None) or app.notes
            if job_description:
                # Simple keyword extraction
                common_skills = [
                    "Python",
                    "JavaScript",
                    "React",
                    "Node.js",
                    "SQL",
                    "AWS",
                    "Docker",
                    "Kubernetes",
                    "Git",
                    "CI/CD",
                    "Agile",
                    "REST API",
                    "TypeScript",
                    "Java",
                    "C++",
                    "Go",
                    "Rust",
                    "MongoDB",
                    "PostgreSQL",
                    "Redis",
                    "GraphQL",
                    "Microservices",
                ]
                for skill in common_skills:
                    if skill.lower() in str(job_description).lower():
                        all_required_skills.append(skill)

        # Count skill frequency
        skill_counts = defaultdict(int)
        for skill in all_required_skills:
            skill_counts[skill] += 1

        # Sort by frequency
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "top_required_skills": [
                {
                    "skill": skill,
                    "count": count,
                    "percentage": round((count / len(applications)) * 100, 1),
                }
                for skill, count in top_skills
            ],
            "total_applications_analyzed": len(applications),
            "ai_powered": False,
            "recommendations": [
                "Consider learning the most frequently requested skills",
                "Update your resume to highlight relevant skills",
                "Take online courses to fill skill gaps",
            ],
        }

    async def get_company_analysis(
        self,
        user_id: str,
        applications: Optional[Sequence[JobApplication]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze applications by company.
        """
        try:
            self._require_applications_or_repository(applications)
            if applications is None:
                assert self.repository is not None
                applications = await self.repository.get_all(user_id=user_id)

            company_stats = defaultdict(
                lambda: {"total": 0, "interviews": 0, "offers": 0, "rejections": 0}
            )

            for app in applications:
                company = app.company or "Unknown"
                company_stats[company]["total"] += 1

                if app.status in [
                    ApplicationStatus.INTERVIEW_SCHEDULED,
                    ApplicationStatus.INTERVIEW_COMPLETED,
                    ApplicationStatus.OFFER_RECEIVED,
                    ApplicationStatus.OFFER_ACCEPTED,
                ]:
                    company_stats[company]["interviews"] += 1

                if app.status in [
                    ApplicationStatus.OFFER_RECEIVED,
                    ApplicationStatus.OFFER_ACCEPTED,
                ]:
                    company_stats[company]["offers"] += 1

                if app.status == ApplicationStatus.REJECTED:
                    company_stats[company]["rejections"] += 1

            # Convert to list and calculate success rates
            company_list = []
            for company, stats in company_stats.items():
                success_rate = (
                    (stats["offers"] / stats["total"] * 100)
                    if stats["total"] > 0
                    else 0
                )
                company_list.append(
                    {
                        "company": company,
                        **stats,
                        "success_rate": round(success_rate, 1),
                    }
                )

            # Sort by total applications
            company_list.sort(key=lambda x: x["total"], reverse=True)

            return {
                "companies": company_list[:20],  # Top 20 companies
                "total_companies": len(company_stats),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing companies: {e}", exc_info=True)
            raise
