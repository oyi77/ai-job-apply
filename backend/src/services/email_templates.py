"""Email templates for job application reminders."""

from datetime import datetime
from typing import Dict, Any
import re


def _sanitize_template_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize template data to prevent template injection attacks.

    Args:
        data: Template data to sanitize

    Returns:
        Sanitized template data
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove any template-like patterns that could be exploited
            # This is a basic safeguard - the template rendering uses f-strings
            # which are safe by design, but we add extra protection
            sanitized[key] = re.sub(r"[{}[\]()\\@#$%^*<>]", "", value)
        else:
            sanitized[key] = value
    return sanitized


class EmailTemplateRenderer:
    """Render email templates with dynamic data."""

    def __init__(self):
        """Initialize template renderer."""
        self.templates = {
            "follow_up_reminder": self._render_follow_up_reminder,
            "status_check_reminder": self._render_status_check_reminder,
            "interview_prep_reminder": self._render_interview_prep_reminder,
            "password_reset": self._render_password_reset,
            "application_confirmation": self._render_application_confirmation,
            "welcome": self._render_welcome,
        }

    async def render(
        self, template_name: str, data: Dict[str, Any]
    ) -> tuple[str, str, str]:
        """Render email template.

        Args:
            template_name: Name of the template
            data: Template data

        Returns:
            Tuple of (subject, body_html, body_text)
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")

        # Sanitize data to prevent template injection
        sanitized_data = _sanitize_template_data(data)

        return await self.templates[template_name](sanitized_data)

    async def _render_follow_up_reminder(
        self, data: Dict[str, Any]
    ) -> tuple[str, str, str]:
        """Render follow-up reminder email."""
        job_title = data.get("job_title", "the position")
        company = data.get("company", "the company")
        application_date = data.get("application_date", "recently")
        user_name = data.get("user_name", "there")
        application_id = data.get("application_id", "")

        subject = f"Follow up on your application to {company}"

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4a90d9; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #4a90d9; color: white; text-decoration: none; border-radius: 4px; margin-top: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Job Application Follow-Up</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>It's been about a week since you applied to <strong>{job_title}</strong> at <strong>{company}</strong>.</p>
                    <p>This is a good time to follow up on your application. Here are some suggestions:</p>
                    <ul>
                        <li>Check the job posting for any updates or new requirements</li>
                        <li>Prepare for potential phone or video interviews</li>
                        <li>Research the company further and prepare thoughtful questions</li>
                        <li>Connect with employees at the company on LinkedIn</li>
                    </ul>
                    <p>Remember to be patient - the hiring process can take time.</p>
                    <a href="{data.get("app_url", "#")}/applications/{application_id}" class="button">View Application</a>
                </div>
                <div class="footer">
                    <p>This is an automated reminder from your AI Job Application Assistant.</p>
                    <p>To manage your reminder preferences, visit your account settings.</p>
                </div>
            </div>
        </body>
        </html>
        """

        body_text = f"""
        Hi {user_name},

        It's been about a week since you applied to {job_title} at {company}.

        This is a good time to follow up on your application. Here are some suggestions:
        - Check the job posting for any updates or new requirements
        - Prepare for potential phone or video interviews
        - Research the company further and prepare thoughtful questions
        - Connect with employees at the company on LinkedIn

        Remember to be patient - the hiring process can take time.

        View your application: {data.get("app_url", "#")}/applications/{application_id}

        ---
        This is an automated reminder from your AI Job Application Assistant.
        To manage your reminder preferences, visit your account settings.
        """

        return subject, body_html, body_text

    async def _render_status_check_reminder(
        self, data: Dict[str, Any]
    ) -> tuple[str, str, str]:
        """Render status check reminder email."""
        job_title = data.get("job_title", "the position")
        company = data.get("company", "the company")
        last_update = data.get("last_update", "recently")
        user_name = data.get("user_name", "there")
        application_id = data.get("application_id", "")

        subject = f"Check in on your application to {company}"

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f0ad4e; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #f0ad4e; color: white; text-decoration: none; border-radius: 4px; margin-top: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Application Status Check</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>It's been a couple of weeks since you applied to <strong>{job_title}</strong> at <strong>{company}</strong>.</p>
                    <p>If you haven't heard back yet, don't worry - hiring processes can be lengthy. However, here are some things to consider:</p>
                    <ul>
                        <li>Is it time to reach out to the hiring manager?</li>
                        <li>Have you applied to similar positions at other companies?</li>
                        <li>Should you update your resume or cover letter?</li>
                    </ul>
                    <p>Keep up the momentum in your job search!</p>
                    <a href="{data.get("app_url", "#")}/applications/{application_id}" class="button">Check Application Status</a>
                </div>
                <div class="footer">
                    <p>This is an automated reminder from your AI Job Application Assistant.</p>
                    <p>To manage your reminder preferences, visit your account settings.</p>
                </div>
            </div>
        </body>
        </html>
        """

        body_text = f"""
        Hi {user_name},

        It's been a couple of weeks since you applied to {job_title} at {company}.

        If you haven't heard back yet, don't worry - hiring processes can be lengthy. However, here are some things to consider:
        - Is it time to reach out to the hiring manager?
        - Have you applied to similar positions at other companies?
        - Should you update your resume or cover letter?

        Keep up the momentum in your job search!

        Check your application status: {data.get("app_url", "#")}/applications/{application_id}

        ---
        This is an automated reminder from your AI Job Application Assistant.
        To manage your reminder preferences, visit your account settings.
        """

        return subject, body_html, body_text

    async def _render_interview_prep_reminder(
        self, data: Dict[str, Any]
    ) -> tuple[str, str, str]:
        """Render interview preparation reminder email."""
        job_title = data.get("job_title", "the position")
        company = data.get("company", "the company")
        interview_date = data.get("interview_date", "soon")
        user_name = data.get("user_name", "there")
        application_id = data.get("application_id", "")

        subject = f"Interview Preparation: {job_title} at {company}"

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #5cb85c; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #5cb85c; color: white; text-decoration: none; border-radius: 4px; margin-top: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .tips {{ background-color: #fff; padding: 15px; border-left: 4px solid #5cb85c; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Interview Prep Reminder 🎯</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>You have an interview coming up for <strong>{job_title}</strong> at <strong>{company}</strong> on <strong>{interview_date}</strong>!</p>
                    
                    <div class="tips">
                        <h3>Quick Preparation Tips:</h3>
                        <ul>
                            <li>Research the company culture and recent news</li>
                            <li>Review the job description and match your experience</li>
                            <li>Prepare answers to common interview questions</li>
                            <li>Have questions ready for the interviewer</li>
                            <li>Test your video/phone setup if it's remote</li>
                            <li>Plan your outfit and background</li>
                        </ul>
                    </div>
                    
                    <p>Your AI Assistant can help you prepare - try the Interview Prep feature!</p>
                    <a href="{data.get("app_url", "#")}/applications/{application_id}/interview-prep" class="button">Prepare for Interview</a>
                </div>
                <div class="footer">
                    <p>Good luck with your interview! 🍀</p>
                    <p>This is an automated reminder from your AI Job Application Assistant.</p>
                </div>
            </div>
        </body>
        </html>
        """

        body_text = f"""
        Hi {user_name},

        You have an interview coming up for {job_title} at {company} on {interview_date}!

        Quick Preparation Tips:
        - Research the company culture and recent news
        - Review the job description and match your experience
        - Prepare answers to common interview questions
        - Have questions ready for the interviewer
        - Test your video/phone setup if it's remote
        - Plan your outfit and background

        Your AI Assistant can help you prepare - try the Interview Prep feature!

        Prepare for interview: {data.get("app_url", "#")}/applications/{application_id}/interview-prep

        ---
        Good luck with your interview!
        This is an automated reminder from your AI Job Application Assistant.
        """

        return subject, body_html, body_text

    async def _render_password_reset(
        self, data: Dict[str, Any]
    ) -> tuple[str, str, str]:
        """Render password reset email."""
        reset_link = data.get("reset_link", "#")
        user_name = data.get("user_name", "User")
        expiry_hours = data.get("expiry_hours", 1)

        subject = "Reset Your Password"

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #d9534f; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #d9534f; color: white; text-decoration: none; border-radius: 4px; margin-top: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    <p>You have requested to reset your password. Please click the link below to reset it:</p>
                    <a href="{reset_link}" class="button">Reset Password</a>
                    <p>This link will expire in {expiry_hours} hour(s>.</p>
                    <p>If you did not request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from AI Job Application Assistant.</p>
                </div>
            </div>
        </body>
        </html>
        """

        body_text = f"""
        Hello {user_name},

        You have requested to reset your password. Please click the link below to reset it:

        {reset_link}

        This link will expire in {expiry_hours} hour(s).

        If you did not request this, please ignore this email.

        ---
        This is an automated message from AI Job Application Assistant.
        """

        return subject, body_html, body_text

    async def _render_application_confirmation(
        self, data: Dict[str, Any]
    ) -> tuple[str, str, str]:
        """Render application confirmation email."""
        job_title = data.get("job_title", "the position")
        company = data.get("company", "the company")
        user_name = data.get("user_name", "there")
        application_id = data.get("application_id", "")

        subject = f"Application Confirmed: {job_title} at {company}"

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #5cb85c; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #5cb85c; color: white; text-decoration: none; border-radius: 4px; margin-top: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Application Submitted ✅</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>Your application for <strong>{job_title}</strong> at <strong>{company}</strong> has been successfully submitted!</p>
                    <p>What happens next?</p>
                    <ul>
                        <li>You'll receive a confirmation from the company (if available)</li>
                        <li>We'll send you follow-up reminders</li>
                        <li>You can track your application status in your dashboard</li>
                    </ul>
                    <a href="{data.get("app_url", "#")}/applications/{application_id}" class="button">View Application</a>
                </div>
                <div class="footer">
                    <p>Keep applying! Your next opportunity is around the corner.</p>
                </div>
            </div>
        </body>
        </html>
        """

        body_text = f"""
        Hi {user_name},

        Your application for {job_title} at {company} has been successfully submitted!

        What happens next?
        - You'll receive a confirmation from the company (if available)
        - We'll send you follow-up reminders
        - You can track your application status in your dashboard

        View your application: {data.get("app_url", "#")}/applications/{application_id}

        ---
        Keep applying! Your next opportunity is around the corner.
        """

        return subject, body_html, body_text

    async def _render_welcome(self, data: Dict[str, Any]) -> tuple[str, str, str]:
        """Render welcome email for new users."""
        user_name = data.get("user_name", "there")
        app_url = data.get("app_url", "https://app.example.com")

        subject = "Welcome to AI Job Application Assistant! 🎉"

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 30px; background-color: #f9f9f9; border-radius: 0 0 8px 8px; }}
                .feature-list {{ margin: 20px 0; padding-left: 20px; }}
                .feature-list li {{ margin: 10px 0; }}
                .button {{ display: inline-block; padding: 14px 28px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 6px; margin-top: 20px; font-weight: bold; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; margin-top: 20px; }}
                .highlight {{ background-color: #fff3cd; padding: 15px; border-radius: 4px; border-left: 4px solid #ffc107; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome Aboard, {user_name}! 🚀</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>Thank you for joining <strong>AI Job Application Assistant</strong>! We're thrilled to have you on board.</p>
                    
                    <div class="highlight">
                        <strong>💡 Pro Tip:</strong> Complete your profile and upload your resume to get personalized job recommendations!
                    </div>
                    
                    <p>Here's what you can do with our platform:</p>
                    <ul class="feature-list">
                        <li>🔍 <strong>Smart Job Search</strong> - Find relevant opportunities across multiple platforms</li>
                        <li>📝 <strong>AI Resume Optimization</strong> - Let AI improve your resume for each application</li>
                        <li>✉️ <strong>Cover Letter Generation</strong> - Create personalized cover letters in seconds</li>
                        <li>📊 <strong>Application Tracking</strong> - Keep all your applications organized in one place</li>
                        <li>⏰ <strong>Smart Reminders</strong> - Never miss a follow-up deadline</li>
                        <li>📈 <strong>Analytics & Insights</strong> - Track your job search performance</li>
                    </ul>
                    
                    <p>Let's get started on landing your dream job!</p>
                    <a href="{app_url}/dashboard" class="button">Go to Dashboard</a>
                </div>
                <div class="footer">
                    <p>Need help? Reply to this email or visit our <a href="{app_url}/help">Help Center</a></p>
                    <p>Happy job hunting! 🎯</p>
                    <p>— The AI Job Application Assistant Team</p>
                </div>
            </div>
        </body>
        </html>
        """

        body_text = f"""
        Welcome Aboard, {user_name}! 🚀
        
        Hi {user_name},
        
        Thank you for joining AI Job Application Assistant! We're thrilled to have you on board.
        
        Here's what you can do with our platform:
        
        • Smart Job Search - Find relevant opportunities across multiple platforms
        • AI Resume Optimization - Let AI improve your resume for each application
        • Cover Letter Generation - Create personalized cover letters in seconds
        • Application Tracking - Keep all your applications organized in one place
        • Smart Reminders - Never miss a follow-up deadline
        • Analytics & Insights - Track your job search performance
        
        Let's get started on landing your dream job!
        
        Go to Dashboard: {app_url}/dashboard
        
        ---
        Need help? Reply to this email or visit our Help Center: {app_url}/help
        
        Happy job hunting! 🎯
        — The AI Job Application Assistant Team
        """

        return subject, body_html, body_text


# Global template renderer
email_template_renderer = EmailTemplateRenderer()
