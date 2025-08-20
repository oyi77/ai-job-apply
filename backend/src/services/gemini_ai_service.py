"""Gemini AI service implementation for the AI Job Application Assistant."""

import asyncio
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime

from ..core.ai_service import AIService
from ..models.resume import ResumeOptimizationRequest, ResumeOptimizationResponse, Resume
from ..models.cover_letter import CoverLetterRequest, CoverLetter
from ..config import config
from loguru import logger


class GeminiAIService(AIService):
    """Concrete implementation of AIService using Google Gemini."""
    
    def __init__(self):
        """Initialize the Gemini AI service."""
        self.logger = logger.bind(module="GeminiAIService")
        self.model = None
        
        # Use main configuration
        self.api_key = config.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"
        self.temperature = 0.7
        self.max_tokens = 2048
        
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Gemini client."""
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    self.model_name,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.temperature,
                        max_output_tokens=self.max_tokens,
                    )
                )
                self.logger.info(f"Gemini AI service initialized: {self.model_name}")
            else:
                self.logger.warning("Gemini API key not configured, running in mock mode")
                self.model = None
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini AI service: {e}")
            self.model = None
    
    async def optimize_resume(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """Optimize resume for a specific job using Gemini AI."""
        try:
            self.logger.info(f"Optimizing resume for {request.target_role} at {request.company_name}")
            
            if not await self.is_available():
                return self._mock_resume_optimization(request)
            
            # Create the optimization prompt
            prompt = self._create_resume_optimization_prompt(request)
            
            # Generate response using Gemini
            response = await self._generate_content(prompt)
            
            if response:
                # Parse the AI response
                optimization_data = self._parse_resume_optimization_response(response)
                
                # Create resume object (mock for now)
                original_resume = Resume(
                    name="Current Resume",
                    file_path=f"./resumes/{request.resume_id}.pdf",
                    file_type="pdf"
                )
                
                return ResumeOptimizationResponse(
                    original_resume=original_resume,
                    optimized_content=optimization_data.get("optimized_content", ""),
                    suggestions=optimization_data.get("suggestions", []),
                    skill_gaps=optimization_data.get("skill_gaps", []),
                    improvements=optimization_data.get("improvements", []),
                    confidence_score=optimization_data.get("confidence_score", 0.8)
                )
            else:
                return self._mock_resume_optimization(request)
                
        except Exception as e:
            self.logger.error(f"Error optimizing resume: {e}", exc_info=True)
            return self._mock_resume_optimization(request)
    
    async def generate_cover_letter(self, request: CoverLetterRequest) -> CoverLetter:
        """Generate a personalized cover letter using Gemini AI."""
        try:
            self.logger.info(f"Generating cover letter for {request.job_title} at {request.company_name}")
            
            if not await self.is_available():
                return self._mock_cover_letter_generation(request)
            
            # Create the cover letter prompt
            prompt = self._create_cover_letter_prompt(request)
            
            # Generate response using Gemini
            response = await self._generate_content(prompt)
            
            if response:
                # Parse the AI response
                cover_letter_data = self._parse_cover_letter_response(response)
                
                return CoverLetter(
                    job_title=request.job_title,
                    company_name=request.company_name,
                    content=cover_letter_data.get("content", ""),
                    tone=request.tone,
                    word_count=len(cover_letter_data.get("content", "").split())
                )
            else:
                return self._mock_cover_letter_generation(request)
                
        except Exception as e:
            self.logger.error(f"Error generating cover letter: {e}", exc_info=True)
            return self._mock_cover_letter_generation(request)
    
    async def analyze_job_match(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        """Analyze how well a resume matches a job description using Gemini AI."""
        try:
            self.logger.info("Analyzing job match using Gemini AI")
            
            if not await self.is_available():
                return self._mock_job_match_analysis()
            
            # Create the job match analysis prompt
            prompt = self._create_job_match_prompt(resume_content, job_description)
            
            # Generate response using Gemini
            response = await self._generate_content(prompt)
            
            if response:
                return self._parse_job_match_response(response)
            else:
                return self._mock_job_match_analysis()
                
        except Exception as e:
            self.logger.error(f"Error analyzing job match: {e}", exc_info=True)
            return self._mock_job_match_analysis()
    
    async def extract_resume_skills(self, resume_content: str) -> List[str]:
        """Extract skills from resume content using Gemini AI."""
        try:
            self.logger.info("Extracting skills from resume using Gemini AI")
            
            if not await self.is_available():
                return self._mock_skills_extraction()
            
            # Create the skills extraction prompt
            prompt = f"""
            Extract all technical skills, soft skills, tools, and technologies mentioned in this resume.
            Return only a JSON array of skills.
            
            Resume content:
            {resume_content}
            
            Response format: ["skill1", "skill2", "skill3"]
            """
            
            # Generate response using Gemini
            response = await self._generate_content(prompt)
            
            if response:
                try:
                    skills = json.loads(response)
                    return skills if isinstance(skills, list) else []
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract skills from text
                    return self._extract_skills_from_text(response)
            else:
                return self._mock_skills_extraction()
                
        except Exception as e:
            self.logger.error(f"Error extracting skills: {e}", exc_info=True)
            return self._mock_skills_extraction()
    
    async def suggest_resume_improvements(self, resume_content: str, job_description: str) -> List[str]:
        """Suggest improvements for a resume based on job description using Gemini AI."""
        try:
            self.logger.info("Generating resume improvement suggestions using Gemini AI")
            
            if not await self.is_available():
                return self._mock_improvement_suggestions()
            
            # Create the improvement suggestions prompt
            prompt = f"""
            Analyze this resume against the job description and provide specific improvement suggestions.
            Return only a JSON array of actionable suggestions.
            
            Resume content:
            {resume_content}
            
            Job description:
            {job_description}
            
            Response format: ["suggestion1", "suggestion2", "suggestion3"]
            """
            
            # Generate response using Gemini
            response = await self._generate_content(prompt)
            
            if response:
                try:
                    suggestions = json.loads(response)
                    return suggestions if isinstance(suggestions, list) else []
                except json.JSONDecodeError:
                    # If JSON parsing fails, extract suggestions from text
                    return self._extract_suggestions_from_text(response)
            else:
                return self._mock_improvement_suggestions()
                
        except Exception as e:
            self.logger.error(f"Error generating improvement suggestions: {e}", exc_info=True)
            return self._mock_improvement_suggestions()
    
    async def is_available(self) -> bool:
        """Check if the Gemini AI service is available."""
        return self.model is not None and self.api_key is not None
    
    async def _generate_content(self, prompt: str) -> Optional[str]:
        """Generate content using Gemini AI."""
        try:
            if not self.model:
                return None
            
            # Run the synchronous API call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=config.TEMPERATURE,
                        max_output_tokens=config.MAX_TOKENS,
                    )
                )
            )
            
            return response.text if response and response.text else None
            
        except Exception as e:
            self.logger.error(f"Error generating content with Gemini: {e}", exc_info=True)
            return None
    
    def _create_resume_optimization_prompt(self, request: ResumeOptimizationRequest) -> str:
        """Create a prompt for resume optimization."""
        return f"""
        You are an expert resume optimizer. Optimize the following resume for the target role and company.
        
        Target Role: {request.target_role}
        Company: {request.company_name or 'Not specified'}
        Job Description: {request.job_description}
        
        Please provide a JSON response with the following structure:
        {{
            "optimized_content": "The optimized resume content",
            "suggestions": ["suggestion1", "suggestion2"],
            "skill_gaps": ["missing_skill1", "missing_skill2"],
            "improvements": ["improvement1", "improvement2"],
            "confidence_score": 0.85
        }}
        
        Focus on:
        - Tailoring the resume to match the job requirements
        - Highlighting relevant skills and experience
        - Improving formatting and readability
        - Adding quantifiable achievements
        - Identifying skill gaps
        """
    
    def _create_cover_letter_prompt(self, request: CoverLetterRequest) -> str:
        """Create a prompt for cover letter generation."""
        return f"""
        You are an expert cover letter writer. Generate a personalized cover letter for the following job application.
        
        Job Title: {request.job_title}
        Company: {request.company_name}
        Job Description: {request.job_description}
        Resume Summary: {request.resume_summary}
        Tone: {request.tone}
        Focus Areas: {', '.join(request.focus_areas or [])}
        Custom Instructions: {request.custom_instructions or 'None'}
        
        Please provide a JSON response with the following structure:
        {{
            "content": "The complete cover letter content"
        }}
        
        The cover letter should:
        - Be professional and engaging
        - Match the specified tone
        - Highlight relevant experience from the resume summary
        - Address the specific job requirements
        - Be 3-4 paragraphs long
        - Include a strong opening and closing
        """
    
    def _create_job_match_prompt(self, resume_content: str, job_description: str) -> str:
        """Create a prompt for job match analysis."""
        return f"""
        Analyze how well this resume matches the job description. Provide a detailed analysis.
        
        Resume Content: {resume_content}
        Job Description: {job_description}
        
        Please provide a JSON response with the following structure:
        {{
            "overall_match_score": 0.78,
            "skills_match": {{
                "required_skills": ["skill1", "skill2"],
                "matching_skills": ["skill1"],
                "missing_skills": ["skill2"],
                "skills_score": 0.67
            }},
            "experience_match": {{
                "required_years": 3,
                "candidate_years": 4,
                "experience_score": 0.85
            }},
            "recommendations": ["recommendation1", "recommendation2"],
            "confidence": 0.82
        }}
        """
    
    def _parse_resume_optimization_response(self, response: str) -> Dict[str, Any]:
        """Parse the resume optimization response from Gemini."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            return {
                "optimized_content": response[:500] + "...",
                "suggestions": ["Add more specific achievements", "Improve formatting"],
                "skill_gaps": ["Technical skills", "Certifications"],
                "improvements": ["Enhanced content", "Better structure"],
                "confidence_score": 0.75
            }
    
    def _parse_cover_letter_response(self, response: str) -> Dict[str, Any]:
        """Parse the cover letter response from Gemini."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {"content": response}
    
    def _parse_job_match_response(self, response: str) -> Dict[str, Any]:
        """Parse the job match analysis response from Gemini."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing
            return {
                "overall_match_score": 0.75,
                "skills_match": {
                    "required_skills": ["Python", "JavaScript"],
                    "matching_skills": ["Python"],
                    "missing_skills": ["JavaScript"],
                    "skills_score": 0.5
                },
                "experience_match": {
                    "required_years": 3,
                    "candidate_years": 2,
                    "experience_score": 0.67
                },
                "recommendations": ["Highlight relevant projects", "Add missing skills"],
                "confidence": 0.7
            }
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text response."""
        # Simple skill extraction fallback
        common_skills = [
            "Python", "JavaScript", "Java", "React", "Node.js", "SQL", 
            "Git", "Docker", "AWS", "Machine Learning", "Data Analysis"
        ]
        return [skill for skill in common_skills if skill.lower() in text.lower()]
    
    def _extract_suggestions_from_text(self, text: str) -> List[str]:
        """Extract suggestions from text response."""
        # Simple suggestion extraction fallback
        lines = text.split('\n')
        suggestions = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                suggestions.append(line.lstrip('-•* '))
        return suggestions[:5]  # Limit to 5 suggestions
    
    # Mock methods for fallback functionality
    def _mock_resume_optimization(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """Mock resume optimization response."""
        original_resume = Resume(
            name="Current Resume",
            file_path=f"./resumes/{request.resume_id}.pdf",
            file_type="pdf"
        )
        
        return ResumeOptimizationResponse(
            original_resume=original_resume,
            optimized_content=f"Optimized resume for {request.target_role} position...",
            suggestions=[
                "Add more specific technical skills",
                "Include quantifiable achievements",
                "Tailor experience descriptions to match job requirements"
            ],
            skill_gaps=["Cloud computing", "Machine learning"],
            improvements=[
                "Enhanced technical skills section",
                "Added project-based achievements",
                "Improved formatting and readability"
            ],
            confidence_score=0.85
        )
    
    def _mock_cover_letter_generation(self, request: CoverLetterRequest) -> CoverLetter:
        """Mock cover letter generation response."""
        content = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {request.job_title} position at {request.company_name}. 
Based on the job description, I believe my background and skills align perfectly with your requirements.

{request.resume_summary}

I am particularly excited about the opportunity to contribute to {request.company_name}'s innovative projects 
and would welcome the chance to discuss how my experience can benefit your team.

Thank you for considering my application. I look forward to the opportunity to speak with you further.

Best regards,
[Your Name]"""
        
        return CoverLetter(
            job_title=request.job_title,
            company_name=request.company_name,
            content=content,
            tone=request.tone,
            word_count=len(content.split())
        )
    
    def _mock_job_match_analysis(self) -> Dict[str, Any]:
        """Mock job match analysis response."""
        return {
            "overall_match_score": 0.78,
            "skills_match": {
                "required_skills": ["Python", "JavaScript", "React"],
                "matching_skills": ["Python", "JavaScript"],
                "missing_skills": ["React"],
                "skills_score": 0.67
            },
            "experience_match": {
                "required_years": 3,
                "candidate_years": 4,
                "experience_score": 0.85
            },
            "recommendations": [
                "Highlight React experience if available",
                "Emphasize project-based achievements",
                "Include specific technical accomplishments"
            ],
            "confidence": 0.82
        }
    
    def _mock_skills_extraction(self) -> List[str]:
        """Mock skills extraction response."""
        return ["Python", "JavaScript", "SQL", "Git", "Docker", "AWS", "React", "Node.js"]
    
    def _mock_improvement_suggestions(self) -> List[str]:
        """Mock improvement suggestions response."""
        return [
            "Add specific metrics for project achievements",
            "Include relevant certifications",
            "Highlight leadership experience",
            "Use consistent bullet point formatting",
            "Add industry-specific keywords"
        ]
