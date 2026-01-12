"""
AI-Powered Insights for Analytics

Generates intelligent insights and recommendations based on analytics data.
"""

from typing import Dict, Any, List
from loguru import logger

from src.services.analytics_service import AnalyticsService
from src.services.ai_service import ModernAIService


class AnalyticsInsightsService:
    """Generate AI-powered insights from analytics data."""
    
    def __init__(self, analytics_service: AnalyticsService, ai_service: ModernAIService):
        """Initialize insights service."""
        self.analytics_service = analytics_service
        self.ai_service = ai_service
        self.logger = logger.bind(module="AnalyticsInsightsService")
    
    async def generate_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive insights based on user's analytics.
        
        Args:
            user_id: User ID to analyze
            
        Returns:
            Dictionary with insights and recommendations
        """
        try:
            # Gather analytics data
            success_rate = await self.analytics_service.get_application_success_rate(user_id)
            response_time = await self.analytics_service.get_response_time_analysis(user_id)
            interview_perf = await self.analytics_service.get_interview_performance(user_id)
            skills_gap = await self.analytics_service.get_skills_gap_analysis(user_id)
            companies = await self.analytics_service.get_company_analysis(user_id)
            
            # Generate insights
            insights = []
            recommendations = []
            
            # Success rate insights
            if success_rate["success_rate"] < 10:
                insights.append({
                    "type": "warning",
                    "category": "success_rate",
                    "message": f"Your success rate is {success_rate['success_rate']}%, which is below average. Consider refining your application strategy.",
                    "priority": "high"
                })
                recommendations.append({
                    "category": "application_quality",
                    "suggestion": "Focus on quality over quantity - tailor each application to the specific role",
                    "impact": "high"
                })
            elif success_rate["success_rate"] > 20:
                insights.append({
                    "type": "success",
                    "category": "success_rate",
                    "message": f"Great job! Your {success_rate['success_rate']}% success rate is above average.",
                    "priority": "low"
                })
            
            # Interview conversion insights
            if interview_perf["total_interviews"] > 0:
                conversion_rate = interview_perf["interview_to_offer_rate"]
                if conversion_rate < 30:
                    insights.append({
                        "type": "warning",
                        "category": "interview_performance",
                        "message": f"Your interview-to-offer rate is {conversion_rate}%. Consider improving interview skills.",
                        "priority": "high"
                    })
                    recommendations.append({
                        "category": "interview_prep",
                        "suggestion": "Practice common interview questions and work on your communication skills",
                        "impact": "high"
                    })
            
            # Response time insights
            if response_time["avg_response_time_days"] > 14:
                insights.append({
                    "type": "info",
                    "category": "response_time",
                    "message": f"Companies are taking an average of {response_time['avg_response_time_days']} days to respond. This is normal for many industries.",
                    "priority": "low"
                })
            
            # Skills gap insights
            if skills_gap.get("top_required_skills"):
                top_skills = skills_gap["top_required_skills"][:3]
                skills_list = [s["skill"] for s in top_skills]
                insights.append({
                    "type": "info",
                    "category": "skills",
                    "message": f"Most requested skills in your applications: {', '.join(skills_list)}",
                    "priority": "medium"
                })
                recommendations.append({
                    "category": "skill_development",
                    "suggestion": f"Consider strengthening your expertise in: {', '.join(skills_list)}",
                    "impact": "medium"
                })
            
            # Company insights
            if companies.get("companies"):
                top_companies = companies["companies"][:3]
                for company in top_companies:
                    if company["total"] > 3 and company["success_rate"] == 0:
                        insights.append({
                            "type": "warning",
                            "category": "company_targeting",
                            "message": f"You've applied to {company['company']} {company['total']} times with no success. Consider trying different companies.",
                            "priority": "medium"
                        })
            
            # Application volume insights
            total_apps = success_rate["total_applications"]
            if total_apps < 10:
                recommendations.append({
                    "category": "application_volume",
                    "suggestion": "Increase your application volume to improve your chances",
                    "impact": "high"
                })
            elif total_apps > 100:
                recommendations.append({
                    "category": "application_strategy",
                    "suggestion": "You're applying to many positions. Consider being more selective and tailoring applications",
                    "impact": "medium"
                })
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "summary": {
                    "total_insights": len(insights),
                    "high_priority_count": sum(1 for i in insights if i["priority"] == "high"),
                    "recommendations_count": len(recommendations)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}", exc_info=True)
            raise
    
    async def generate_ai_recommendations(self, user_id: str) -> List[str]:
        """
        Generate AI-powered recommendations using the AI service.
        
        This is a placeholder for future AI integration.
        """
        try:
            # For now, return rule-based recommendations
            # In the future, this could use the AI service to generate personalized recommendations
            
            success_rate = await self.analytics_service.get_application_success_rate(user_id)
            
            recommendations = []
            
            if success_rate["success_rate"] < 15:
                recommendations.append("Consider getting your resume professionally reviewed")
                recommendations.append("Research companies thoroughly before applying")
                recommendations.append("Network with employees at target companies")
            
            if success_rate["interview_rate"] < 20:
                recommendations.append("Optimize your resume keywords for ATS systems")
                recommendations.append("Ensure your LinkedIn profile is complete and matches your resume")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating AI recommendations: {e}", exc_info=True)
            return []
