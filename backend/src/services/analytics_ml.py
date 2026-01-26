"""
ML Statistical Trends Service for Job Application Analytics

Provides statistical analysis and trend predictions including:
- Time series forecasting for application success
- Statistical trend detection
- Predictive analytics for job search outcomes
- Pattern recognition in application data
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import statistics
from loguru import logger

from src.models.application import JobApplication, ApplicationStatus
from src.database.repositories.application_repository import ApplicationRepository


class AnalyticsMLService:
    """Service for ML-powered statistical analysis and trend predictions."""

    def __init__(self, repository: Optional[ApplicationRepository] = None):
        """Initialize ML analytics service."""
        self.repository = repository
        self.logger = logger.bind(module="AnalyticsMLService")

    async def predict_success_probability(
        self,
        user_id: str,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
        days_lookback: int = 90,
    ) -> Dict[str, Any]:
        """
        Predict probability of success for future applications.

        Uses historical data to calculate success probability based on:
        - Past success rates
        - Job title patterns
        - Company patterns
        - Time-based trends

        Args:
            user_id: User ID to analyze
            job_title: Optional job title to predict for
            company_name: Optional company to predict for
            days_lookback: Number of days of historical data to use

        Returns:
            Dictionary with success probability and confidence metrics
        """
        try:
            # Get historical applications
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days_lookback)

            applications = await self.repository.get_all(user_id=user_id)
            applications = [app for app in applications if app.created_at >= start_date]

            if not applications:
                return {
                    "success_probability": 0.0,
                    "confidence": 0.0,
                    "sample_size": 0,
                    "recommendation": "Insufficient data for prediction",
                }

            # Calculate base success rate
            total = len(applications)
            successful = sum(
                1
                for app in applications
                if app.status
                in [ApplicationStatus.OFFER_RECEIVED, ApplicationStatus.OFFER_ACCEPTED]
            )
            base_success_rate = successful / total if total > 0 else 0.0

            # Adjust for job title if provided
            title_adjustment = 0.0
            if job_title:
                title_apps = [
                    app
                    for app in applications
                    if app.job_title and job_title.lower() in app.job_title.lower()
                ]
                if title_apps:
                    title_successful = sum(
                        1
                        for app in title_apps
                        if app.status
                        in [
                            ApplicationStatus.OFFER_RECEIVED,
                            ApplicationStatus.OFFER_ACCEPTED,
                        ]
                    )
                    title_rate = title_successful / len(title_apps)
                    title_adjustment = (title_rate - base_success_rate) * 0.3

            # Adjust for company if provided
            company_adjustment = 0.0
            if company_name:
                company_apps = [
                    app
                    for app in applications
                    if app.company_name
                    and company_name.lower() in app.company_name.lower()
                ]
                if company_apps:
                    company_successful = sum(
                        1
                        for app in company_apps
                        if app.status
                        in [
                            ApplicationStatus.OFFER_RECEIVED,
                            ApplicationStatus.OFFER_ACCEPTED,
                        ]
                    )
                    company_rate = company_successful / len(company_apps)
                    company_adjustment = (company_rate - base_success_rate) * 0.2

            # Calculate final probability
            final_probability = min(
                1.0, max(0.0, base_success_rate + title_adjustment + company_adjustment)
            )

            # Calculate confidence based on sample size
            confidence = min(1.0, total / 50)  # Full confidence at 50+ applications

            # Generate recommendation
            if final_probability >= 0.7:
                recommendation = "High success probability - strong match"
            elif final_probability >= 0.4:
                recommendation = "Moderate success probability - good opportunity"
            elif final_probability >= 0.2:
                recommendation = (
                    "Lower success probability - consider skill development"
                )
            else:
                recommendation = (
                    "Low success probability - may need strategy adjustment"
                )

            return {
                "success_probability": round(final_probability * 100, 2),
                "confidence": round(confidence * 100, 2),
                "sample_size": total,
                "base_success_rate": round(base_success_rate * 100, 2),
                "title_adjustment": round(title_adjustment * 100, 2)
                if job_title
                else None,
                "company_adjustment": round(company_adjustment * 100, 2)
                if company_name
                else None,
                "recommendation": recommendation,
            }

        except Exception as e:
            self.logger.error(
                f"Error predicting success probability: {e}", exc_info=True
            )
            raise

    async def detect_trends(
        self, user_id: str, metric: str = "success_rate", days_lookback: int = 90
    ) -> Dict[str, Any]:
        """
        Detect statistical trends in application data.

        Args:
            user_id: User ID to analyze
            metric: Metric to analyze (success_rate, response_time, interview_rate)
            days_lookback: Number of days to analyze

        Returns:
            Dictionary with trend analysis and predictions
        """
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days_lookback)

            applications = await self.repository.get_all(user_id=user_id)
            applications = [app for app in applications if app.created_at >= start_date]

            if len(applications) < 5:
                return {
                    "trend": "insufficient_data",
                    "direction": "unknown",
                    "strength": 0.0,
                    "prediction": "Need more data for trend analysis",
                }

            # Group by week
            weekly_metrics = self._calculate_weekly_metrics(applications, metric)

            if len(weekly_metrics) < 2:
                return {
                    "trend": "insufficient_data",
                    "direction": "unknown",
                    "strength": 0.0,
                    "prediction": "Need more weeks of data",
                }

            # Calculate trend using simple linear regression
            trend_direction, trend_strength = self._calculate_trend(weekly_metrics)

            # Generate prediction
            if trend_direction == "improving":
                prediction = (
                    f"{metric.replace('_', ' ').title()} is improving over time"
                )
            elif trend_direction == "declining":
                prediction = f"{metric.replace('_', ' ').title()} is declining - consider strategy adjustment"
            else:
                prediction = f"{metric.replace('_', ' ').title()} is stable"

            return {
                "trend": trend_direction,
                "direction": trend_direction,
                "strength": round(trend_strength * 100, 2),
                "weekly_data": weekly_metrics,
                "prediction": prediction,
                "sample_weeks": len(weekly_metrics),
            }

        except Exception as e:
            self.logger.error(f"Error detecting trends: {e}", exc_info=True)
            raise

    async def forecast_applications(
        self, user_id: str, weeks_ahead: int = 4
    ) -> Dict[str, Any]:
        """
        Forecast future application metrics.

        Args:
            user_id: User ID to analyze
            weeks_ahead: Number of weeks to forecast

        Returns:
            Dictionary with forecasted metrics
        """
        try:
            # Get last 12 weeks of data
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=84)  # 12 weeks

            applications = await self.repository.get_all(user_id=user_id)
            applications = [app for app in applications if app.created_at >= start_date]

            if len(applications) < 5:
                return {
                    "forecast": [],
                    "confidence": 0.0,
                    "message": "Insufficient data for forecasting",
                }

            # Calculate weekly application counts
            weekly_counts = self._calculate_weekly_application_counts(applications)

            if len(weekly_counts) < 3:
                return {
                    "forecast": [],
                    "confidence": 0.0,
                    "message": "Need at least 3 weeks of data",
                }

            # Calculate average and trend
            avg_applications = statistics.mean(weekly_counts)
            trend_slope = self._calculate_simple_slope(weekly_counts)

            # Generate forecast
            forecast = []
            for week in range(1, weeks_ahead + 1):
                predicted_count = max(0, avg_applications + (trend_slope * week))
                forecast.append(
                    {
                        "week": week,
                        "predicted_applications": round(predicted_count, 1),
                        "lower_bound": max(0, round(predicted_count * 0.7, 1)),
                        "upper_bound": round(predicted_count * 1.3, 1),
                    }
                )

            # Calculate confidence based on data consistency
            if len(weekly_counts) > 1:
                std_dev = statistics.stdev(weekly_counts)
                coefficient_of_variation = (
                    std_dev / avg_applications if avg_applications > 0 else 1.0
                )
                confidence = max(0.0, min(1.0, 1.0 - coefficient_of_variation))
            else:
                confidence = 0.5

            return {
                "forecast": forecast,
                "confidence": round(confidence * 100, 2),
                "historical_average": round(avg_applications, 1),
                "trend": "increasing"
                if trend_slope > 0
                else "decreasing"
                if trend_slope < 0
                else "stable",
                "sample_weeks": len(weekly_counts),
            }

        except Exception as e:
            self.logger.error(f"Error forecasting applications: {e}", exc_info=True)
            raise

    async def analyze_patterns(
        self, user_id: str, days_lookback: int = 90
    ) -> Dict[str, Any]:
        """
        Analyze patterns in application data.

        Identifies:
        - Best days of week to apply
        - Optimal application frequency
        - Success patterns by job type

        Args:
            user_id: User ID to analyze
            days_lookback: Number of days to analyze

        Returns:
            Dictionary with pattern analysis
        """
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days_lookback)

            applications = await self.repository.get_all(user_id=user_id)
            applications = [app for app in applications if app.created_at >= start_date]

            if not applications:
                return {
                    "patterns": [],
                    "recommendations": ["Apply to more positions to identify patterns"],
                }

            # Analyze day of week patterns
            day_patterns = self._analyze_day_patterns(applications)

            # Analyze application frequency
            frequency_pattern = self._analyze_frequency_pattern(applications)

            # Analyze job title patterns
            title_patterns = self._analyze_title_patterns(applications)

            # Generate recommendations
            recommendations = []
            if day_patterns.get("best_day"):
                recommendations.append(
                    f"Consider applying on {day_patterns['best_day']} for better results"
                )
            if frequency_pattern.get("optimal_weekly"):
                recommendations.append(
                    f"Optimal application rate: {frequency_pattern['optimal_weekly']} per week"
                )
            if title_patterns.get("top_success_title"):
                recommendations.append(
                    f"Focus on {title_patterns['top_success_title']} roles"
                )

            return {
                "day_of_week_patterns": day_patterns,
                "frequency_patterns": frequency_pattern,
                "job_title_patterns": title_patterns,
                "recommendations": recommendations,
                "sample_size": len(applications),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing patterns: {e}", exc_info=True)
            raise

    # Helper methods

    def _calculate_weekly_metrics(
        self, applications: List[JobApplication], metric: str
    ) -> List[Dict[str, Any]]:
        """Calculate weekly metrics for trend analysis."""
        weekly_data = defaultdict(
            lambda: {"total": 0, "successful": 0, "interviews": 0}
        )

        for app in applications:
            week_start = app.created_at - timedelta(days=app.created_at.weekday())
            week_key = week_start.strftime("%Y-%m-%d")

            weekly_data[week_key]["total"] += 1

            if app.status in [
                ApplicationStatus.OFFER_RECEIVED,
                ApplicationStatus.OFFER_ACCEPTED,
            ]:
                weekly_data[week_key]["successful"] += 1

            if app.status in [
                ApplicationStatus.INTERVIEW_SCHEDULED,
                ApplicationStatus.INTERVIEW_COMPLETED,
                ApplicationStatus.OFFER_RECEIVED,
                ApplicationStatus.OFFER_ACCEPTED,
            ]:
                weekly_data[week_key]["interviews"] += 1

        # Calculate metric values
        result = []
        for week, data in sorted(weekly_data.items()):
            if metric == "success_rate":
                value = (
                    (data["successful"] / data["total"] * 100)
                    if data["total"] > 0
                    else 0
                )
            elif metric == "interview_rate":
                value = (
                    (data["interviews"] / data["total"] * 100)
                    if data["total"] > 0
                    else 0
                )
            else:
                value = data["total"]

            result.append(
                {
                    "week": week,
                    "value": round(value, 2),
                    "total_applications": data["total"],
                }
            )

        return result

    def _calculate_trend(
        self, weekly_metrics: List[Dict[str, Any]]
    ) -> Tuple[str, float]:
        """Calculate trend direction and strength using simple linear regression."""
        if len(weekly_metrics) < 2:
            return "unknown", 0.0

        values = [m["value"] for m in weekly_metrics]
        n = len(values)

        # Simple linear regression
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(values)

        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable", 0.0

        slope = numerator / denominator

        # Determine direction and strength
        if abs(slope) < 0.5:
            direction = "stable"
            strength = 0.0
        elif slope > 0:
            direction = "improving"
            strength = min(1.0, abs(slope) / 10)
        else:
            direction = "declining"
            strength = min(1.0, abs(slope) / 10)

        return direction, strength

    def _calculate_weekly_application_counts(
        self, applications: List[JobApplication]
    ) -> List[float]:
        """Calculate weekly application counts."""
        weekly_counts = defaultdict(int)

        for app in applications:
            week_start = app.created_at - timedelta(days=app.created_at.weekday())
            week_key = week_start.strftime("%Y-%m-%d")
            weekly_counts[week_key] += 1

        return [count for _, count in sorted(weekly_counts.items())]

    def _calculate_simple_slope(self, values: List[float]) -> float:
        """Calculate simple slope for trend."""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(values)

        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        return numerator / denominator if denominator != 0 else 0.0

    def _analyze_day_patterns(
        self, applications: List[JobApplication]
    ) -> Dict[str, Any]:
        """Analyze patterns by day of week."""
        day_stats = defaultdict(lambda: {"total": 0, "successful": 0})

        for app in applications:
            day_name = app.created_at.strftime("%A")
            day_stats[day_name]["total"] += 1

            if app.status in [
                ApplicationStatus.OFFER_RECEIVED,
                ApplicationStatus.OFFER_ACCEPTED,
            ]:
                day_stats[day_name]["successful"] += 1

        # Calculate success rates
        day_rates = {}
        for day, stats in day_stats.items():
            rate = (
                (stats["successful"] / stats["total"] * 100)
                if stats["total"] > 0
                else 0
            )
            day_rates[day] = {
                "success_rate": round(rate, 2),
                "total_applications": stats["total"],
            }

        # Find best day
        best_day = (
            max(day_rates.items(), key=lambda x: x[1]["success_rate"])[0]
            if day_rates
            else None
        )

        return {"by_day": day_rates, "best_day": best_day}

    def _analyze_frequency_pattern(
        self, applications: List[JobApplication]
    ) -> Dict[str, Any]:
        """Analyze application frequency patterns."""
        if not applications:
            return {}

        # Calculate average applications per week
        days_span = (
            max(app.created_at for app in applications)
            - min(app.created_at for app in applications)
        ).days
        weeks_span = max(1, days_span / 7)
        avg_per_week = len(applications) / weeks_span

        return {
            "average_per_week": round(avg_per_week, 1),
            "optimal_weekly": round(avg_per_week * 1.2, 1),  # Suggest 20% increase
            "total_applications": len(applications),
            "weeks_analyzed": round(weeks_span, 1),
        }

    def _analyze_title_patterns(
        self, applications: List[JobApplication]
    ) -> Dict[str, Any]:
        """Analyze patterns by job title."""
        title_stats = defaultdict(lambda: {"total": 0, "successful": 0})

        for app in applications:
            # Extract key words from job title
            if app.job_title:
                # Simple keyword extraction
                keywords = [
                    "Engineer",
                    "Developer",
                    "Manager",
                    "Analyst",
                    "Designer",
                    "Senior",
                    "Junior",
                ]
                for keyword in keywords:
                    if keyword.lower() in app.job_title.lower():
                        title_stats[keyword]["total"] += 1
                        if app.status in [
                            ApplicationStatus.OFFER_RECEIVED,
                            ApplicationStatus.OFFER_ACCEPTED,
                        ]:
                            title_stats[keyword]["successful"] += 1

        # Calculate success rates
        title_rates = {}
        for title, stats in title_stats.items():
            if stats["total"] >= 2:  # Only include titles with 2+ applications
                rate = (
                    (stats["successful"] / stats["total"] * 100)
                    if stats["total"] > 0
                    else 0
                )
                title_rates[title] = {
                    "success_rate": round(rate, 2),
                    "total_applications": stats["total"],
                }

        # Find top success title
        top_title = (
            max(title_rates.items(), key=lambda x: x[1]["success_rate"])[0]
            if title_rates
            else None
        )

        return {"by_title_keyword": title_rates, "top_success_title": top_title}
