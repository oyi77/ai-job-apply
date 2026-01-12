

@router.get("/export")
async def export_analytics(
    format: str = Query("csv", description="Export format: csv, excel, or pdf"),
    days: int = Query(30, description="Number of days for data"),
    current_user: User = Depends(get_current_user)
):
    """
    Export analytics data in various formats.
    
    Supports CSV, Excel, and PDF formats.
    """
    try:
        analytics_service = AnalyticsService(
            repository=await service_registry.get_application_repository()
        )
        
        # Get dashboard data
        success_rate = await analytics_service.get_application_success_rate(user_id=current_user.id)
        response_time = await analytics_service.get_response_time_analysis(user_id=current_user.id)
        interview_perf = await analytics_service.get_interview_performance(user_id=current_user.id)
        companies = await analytics_service.get_company_analysis(user_id=current_user.id)
        
        # Prepare data for export
        if format.lower() == "pdf":
            # PDF format - structured data
            data = {
                "Success Metrics": success_rate,
                "Response Time Metrics": response_time,
                "Interview Performance": interview_perf
            }
            content = AnalyticsExporter.export_to_pdf(data)
            media_type = "application/pdf"
            filename = f"analytics_report_{datetime.now().strftime('%Y%m%d')}.pdf"
            
        elif format.lower() == "excel":
            # Excel format - company data as table
            data = companies.get("companies", [])
            content = AnalyticsExporter.export_to_excel(data)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"analytics_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
        else:  # CSV (default)
            # CSV format - company data as table
            data = companies.get("companies", [])
            content = AnalyticsExporter.export_to_csv(data)
            media_type = "text/csv"
            filename = f"analytics_report_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export analytics: {str(e)}"
        )
