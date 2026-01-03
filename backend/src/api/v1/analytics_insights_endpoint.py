

@router.get("/insights/ai-recommendations")
async def get_ai_recommendations(
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered insights and recommendations.
    
    Returns:
        Intelligent insights based on analytics patterns
    """
    try:
        analytics_service = AnalyticsService(
            repository=await service_registry.get_application_repository()
        )
        
        ai_service = ModernAIService()
        
        insights_service = AnalyticsInsightsService(
            analytics_service=analytics_service,
            ai_service=ai_service
        )
        
        insights = await insights_service.generate_insights(user_id=current_user.id)
        
        return {"data": insights}
        
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI recommendations"
        )
