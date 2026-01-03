"""Unified AI service that supports multiple providers with fallback."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json

from src.core.ai_service import AIService
from src.models.resume import ResumeOptimizationRequest, ResumeOptimizationResponse, Resume
from src.models.cover_letter import CoverLetterRequest, CoverLetter
from src.models.career_insights import CareerInsightsRequest, CareerInsightsResponse
from src.config import config
from src.services.ai_provider_manager import AIProviderManager
from src.services.gemini_ai_service import GeminiAIService
from loguru import logger


class UnifiedAIService(AIService):
    """Unified AI service that supports multiple providers with intelligent fallback.
    
    Priority order:
    1. Modern providers (Cursor, OpenRouter, OpenAI) via AIProviderManager
    2. Gemini (legacy, but still supported)
    3. Mock responses if all fail
    """
    
    def __init__(self):
        """Initialize the unified AI service."""
        self.logger = logger.bind(module="UnifiedAIService")
        self.provider_manager = AIProviderManager()
        self.gemini_service = GeminiAIService()
        self._initialized = False
        self._use_modern_providers = False
    
    async def initialize(self) -> bool:
        """Initialize the AI service with all available providers."""
        try:
            # Try to initialize modern providers first
            if config.ai_providers:
                success = await self.provider_manager.initialize(config.ai_providers)
                if success and await self.provider_manager.is_any_available():
                    self._use_modern_providers = True
                    self._initialized = True
                    self.logger.info("Unified AI service initialized with modern providers")
                    return True
            
            # Fall back to Gemini if modern providers not available
            if await self.gemini_service.is_available():
                self._use_modern_providers = False
                self._initialized = True
                self.logger.info("Unified AI service initialized with Gemini fallback")
                return True
            
            # No providers available, but service can still work with mocks
            self._initialized = True
            self.logger.warning("No AI providers available, running in mock mode")
            return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize unified AI service: {e}")
            self._initialized = True  # Still allow service to work with mocks
            return False
    
    async def is_available(self) -> bool:
        """Check if any AI provider is available."""
        if not self._initialized:
            return False
        
        if self._use_modern_providers:
            return await self.provider_manager.is_any_available()
        else:
            return await self.gemini_service.is_available()
    
    async def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all AI providers."""
        status = {}
        
        if self._use_modern_providers:
            status.update(await self.provider_manager.get_provider_status())
        
        status["gemini"] = await self.gemini_service.is_available()
        
        return status
    
    async def optimize_resume(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """Optimize resume for a specific job."""
        try:
            self.logger.info(f"Optimizing resume for {request.target_role} at {request.company_name}")
            
            # Try modern providers first
            if self._use_modern_providers and await self.provider_manager.is_any_available():
                try:
                    # Build prompt for resume optimization
                    prompt = self._build_resume_optimization_prompt(request)
                    ai_response = await self.provider_manager.generate_text(prompt)
                    
                    # Parse response
                    optimization_data = self._parse_resume_optimization_response(ai_response.content)
                    
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
                        confidence_score=optimization_data.get("confidence_score", 0.8),
                        ats_score=optimization_data.get("ats_score"),
                        ats_checks=optimization_data.get("ats_checks"),
                        ats_recommendations=optimization_data.get("ats_recommendations")
                    )
                except Exception as e:
                    self.logger.warning(f"Modern provider failed, falling back: {e}")
            
            # Fall back to Gemini
            if await self.gemini_service.is_available():
                return await self.gemini_service.optimize_resume(request)
            
            # Fall back to mock
            return self._mock_resume_optimization(request)
                
        except Exception as e:
            self.logger.error(f"Error optimizing resume: {e}", exc_info=True)
            return self._mock_resume_optimization(request)
    
    async def generate_cover_letter(self, request: CoverLetterRequest) -> CoverLetter:
        """Generate a personalized cover letter."""
        try:
            self.logger.info(f"Generating cover letter for {request.job_title} at {request.company_name}")
            
            # Try modern providers first
            if self._use_modern_providers and await self.provider_manager.is_any_available():
                try:
                    prompt = self._build_cover_letter_prompt(request)
                    ai_response = await self.provider_manager.generate_text(prompt)
                    
                    return CoverLetter(
                        job_title=request.job_title,
                        company_name=request.company_name,
                        content=ai_response.content,
                        tone=request.tone or "professional",
                        word_count=len(ai_response.content.split()),
                        file_path=f"./cover_letters/{request.job_title}_{request.company_name}.txt",
                        generated_at=datetime.now(timezone.utc)
                    )
                except Exception as e:
                    self.logger.warning(f"Modern provider failed, falling back: {e}")
            
            # Fall back to Gemini
            if await self.gemini_service.is_available():
                return await self.gemini_service.generate_cover_letter(request)
            
            # Fall back to mock
            return self._mock_cover_letter_generation(request)
                
        except Exception as e:
            self.logger.error(f"Error generating cover letter: {e}", exc_info=True)
            return self._mock_cover_letter_generation(request)
    
    async def analyze_job_match(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        """Analyze how well a resume matches a job description."""
        try:
            self.logger.info("Analyzing job-resume match")
            
            # Try modern providers first
            if self._use_modern_providers and await self.provider_manager.is_any_available():
                try:
                    prompt = self._build_job_match_prompt(resume_content, job_description)
                    ai_response = await self.provider_manager.generate_text(prompt)
                    return self._parse_job_match_response(ai_response.content)
                except Exception as e:
                    self.logger.warning(f"Modern provider failed, falling back: {e}")
            
            # Fall back to Gemini
            if await self.gemini_service.is_available():
                return await self.gemini_service.analyze_job_match(resume_content, job_description)
            
            # Fall back to mock
            return self._mock_job_match_analysis()
                
        except Exception as e:
            self.logger.error(f"Error analyzing job match: {e}", exc_info=True)
            return self._mock_job_match_analysis()
    
    async def extract_resume_skills(self, resume_content: str) -> List[str]:
        """Extract skills from resume content."""
        try:
            self.logger.info("Extracting skills from resume")
            
            # Try modern providers first
            if self._use_modern_providers and await self.provider_manager.is_any_available():
                try:
                    prompt = f"Extract all technical and professional skills from the following resume content. Return only a JSON array of skill names:\n\n{resume_content}"
                    ai_response = await self.provider_manager.generate_text(prompt)
                    
                    # Try to parse as JSON
                    try:
                        skills = json.loads(ai_response.content)
                        if isinstance(skills, list):
                            return skills
                    except:
                        # If not JSON, split by lines
                        skills = [s.strip() for s in ai_response.content.split('\n') if s.strip()]
                        return skills[:20]  # Limit to 20 skills
                except Exception as e:
                    self.logger.warning(f"Modern provider failed, falling back: {e}")
            
            # Fall back to Gemini
            if await self.gemini_service.is_available():
                return await self.gemini_service.extract_resume_skills(resume_content)
            
            # Fall back to mock
            return self._mock_skills_extraction()
                
        except Exception as e:
            self.logger.error(f"Error extracting skills: {e}", exc_info=True)
            return self._mock_skills_extraction()
    
    async def suggest_resume_improvements(self, resume_content: str, job_description: str) -> List[str]:
        """Suggest improvements for a resume based on job description."""
        try:
            self.logger.info("Generating resume improvement suggestions")
            
            # Try modern providers first
            if self._use_modern_providers and await self.provider_manager.is_any_available():
                try:
                    prompt = f"Analyze this resume and job description, then provide specific improvement suggestions. Return a JSON array of improvement suggestions:\n\nResume:\n{resume_content}\n\nJob Description:\n{job_description}"
                    ai_response = await self.provider_manager.generate_text(prompt)
                    
                    # Try to parse as JSON
                    try:
                        improvements = json.loads(ai_response.content)
                        if isinstance(improvements, list):
                            return improvements
                    except:
                        # If not JSON, split by lines
                        improvements = [s.strip() for s in ai_response.content.split('\n') if s.strip() and s.strip().startswith('-')]
                        return improvements[:10]  # Limit to 10 improvements
                except Exception as e:
                    self.logger.warning(f"Modern provider failed, falling back: {e}")
            
            # Fall back to Gemini
            if await self.gemini_service.is_available():
                return await self.gemini_service.suggest_resume_improvements(resume_content, job_description)
            
            # Fall back to mock
            return self._mock_improvements()
                
        except Exception as e:
            self.logger.error(f"Error suggesting improvements: {e}", exc_info=True)
            return self._mock_improvements()
    
    def _build_resume_optimization_prompt(self, request: ResumeOptimizationRequest) -> str:
        """Build prompt for ATS-optimized resume optimization."""
        return f"""You are an expert ATS (Applicant Tracking System) resume optimizer. 
Optimize this resume for maximum ATS compatibility and job match.

Job Title: {request.target_role}
Company: {request.company_name}
Job Description: {request.job_description}

Resume Content: {request.resume_content[:3000] if request.resume_content else 'Not provided'}

Provide a JSON response with:
{{
    "optimized_content": "ATS-optimized resume content",
    "suggestions": ["specific improvement suggestions"],
    "skill_gaps": ["missing skills from job description"],
    "improvements": ["concrete improvements to make"],
    "ats_score": 0.85,
    "ats_checks": {{
        "keyword_match": 0.90,
        "formatting": 0.85,
        "section_structure": 0.80,
        "contact_info": 0.95
    }},
    "ats_recommendations": [
        "Use standard section headers",
        "Include job description keywords naturally",
        "Use simple formatting without tables",
        "Ensure all text is selectable"
    ],
    "confidence_score": 0.85
}}

ATS Optimization Focus:
1. KEYWORD MATCHING: Extract and naturally integrate keywords from job description
2. FORMATTING: Use standard sections, simple layout, no tables/graphics
3. STRUCTURE: Standard headers (Work Experience, Education, Skills)
4. CONTENT: Quantifiable achievements, action verbs, relevant experience
5. COMPATIBILITY: Ensure resume will parse correctly in ATS systems"""
    
    def _build_cover_letter_prompt(self, request: CoverLetterRequest) -> str:
        """Build prompt for cover letter generation."""
        return f"""Write a professional cover letter for:

Job Title: {request.job_title}
Company: {request.company_name}
Tone: {request.tone or 'professional'}

Resume Summary: {request.resume_content[:500] if request.resume_content else 'Not provided'}

Job Description: {request.job_description}

Write a compelling, personalized cover letter that highlights relevant experience and demonstrates enthusiasm for the role."""
    
    def _build_job_match_prompt(self, resume_content: str, job_description: str) -> str:
        """Build prompt for job match analysis."""
        return f"""Analyze how well this resume matches the job description:

Resume: {resume_content[:1000]}

Job Description: {job_description}

Provide a JSON response with:
- match_percentage (0-100)
- strengths (array)
- weaknesses (array)
- recommendations (array)"""
    
    def _parse_resume_optimization_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response for resume optimization."""
        try:
            # Try to parse as JSON
            data = json.loads(content)
            return {
                "optimized_content": data.get("optimized_content", content),
                "suggestions": data.get("suggestions", []),
                "skill_gaps": data.get("skill_gaps", []),
                "improvements": data.get("improvements", []),
                "confidence_score": data.get("confidence_score", 0.8),
                "ats_score": data.get("ats_score"),
                "ats_checks": data.get("ats_checks"),
                "ats_recommendations": data.get("ats_recommendations", [])
            }
        except:
            # Fallback parsing
            return {
                "optimized_content": content,
                "suggestions": ["Review formatting", "Add more keywords"],
                "skill_gaps": [],
                "improvements": ["Improve structure"],
                "confidence_score": 0.7,
                "ats_score": 0.70,
                "ats_checks": {
                    "keyword_match": 0.65,
                    "formatting": 0.70,
                    "section_structure": 0.75,
                    "contact_info": 0.80
                },
                "ats_recommendations": [
                    "Use standard section headers",
                    "Include job description keywords",
                    "Simplify formatting"
                ]
            }
    
    def _parse_job_match_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response for job match analysis."""
        try:
            data = json.loads(content)
            return {
                "match_percentage": data.get("match_percentage", 70),
                "strengths": data.get("strengths", []),
                "weaknesses": data.get("weaknesses", []),
                "recommendations": data.get("recommendations", [])
            }
        except:
            return {
                "match_percentage": 70,
                "strengths": ["Relevant experience"],
                "weaknesses": ["Some skill gaps"],
                "recommendations": ["Continue learning"]
            }
    
    def _mock_resume_optimization(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """Mock resume optimization response."""
        original_resume = Resume(
            name="Current Resume",
            file_path=f"./resumes/{request.resume_id}.pdf",
            file_type="pdf"
        )
        
        return ResumeOptimizationResponse(
            original_resume=original_resume,
            optimized_content="Mock optimized content - please configure an AI provider",
            suggestions=["Configure an AI provider for real optimization"],
            skill_gaps=[],
            improvements=[],
            confidence_score=0.5
        )
    
    def _mock_cover_letter_generation(self, request: CoverLetterRequest) -> CoverLetter:
        """Mock cover letter generation response."""
        return CoverLetter(
            job_title=request.job_title,
            company_name=request.company_name,
            content="Mock cover letter - please configure an AI provider",
            tone=request.tone or "professional",
            word_count=150,
            file_path=f"./cover_letters/{request.job_title}_{request.company_name}.txt",
            generated_at=datetime.now(timezone.utc)
        )
    
    def _mock_job_match_analysis(self) -> Dict[str, Any]:
        """Mock job match analysis response."""
        return {
            "match_percentage": 60,
            "strengths": ["Some relevant experience"],
            "weaknesses": ["Some skill gaps"],
            "recommendations": ["Continue learning relevant skills"]
        }
    
    def _mock_skills_extraction(self) -> List[str]:
        """Mock skills extraction response."""
        return ["Python", "JavaScript", "Problem Solving"]
    
    def _mock_improvements(self) -> List[str]:
        """Mock improvements response."""
        return ["Add more specific achievements", "Improve formatting"]
    
    async def prepare_interview(self, job_description: str, resume_content: str, company_name: Optional[str] = None, job_title: Optional[str] = None) -> Dict[str, Any]:
        """Prepare interview questions and tips based on job description and resume."""
        try:
            self.logger.info(f"Preparing interview questions for {job_title} at {company_name}")
            
            # Build prompt for interview preparation
            prompt = self._build_interview_prep_prompt(job_description, resume_content, company_name, job_title)
            
            # Try modern providers first
            if self._use_modern_providers and await self.provider_manager.is_any_available():
                try:
                    ai_response = await self.provider_manager.generate_text(prompt)
                    return self._parse_interview_prep_response(ai_response.content)
                except Exception as e:
                    self.logger.warning(f"Modern provider failed for interview prep, falling back: {e}")
            
            # Fall back to Gemini
            if await self.gemini_service.is_available():
                try:
                    return await self.gemini_service.prepare_interview(
                        job_description,
                        resume_content,
                        company_name,
                        job_title
                    )
                except Exception as e:
                    self.logger.warning(f"Gemini failed for interview prep: {e}")
            
            # Fall back to mock
            return self._mock_interview_prep(job_title, company_name)
            
        except Exception as e:
            self.logger.error(f"Error preparing interview: {e}", exc_info=True)
            return self._mock_interview_prep(job_title, company_name)
    
    def _build_interview_prep_prompt(self, job_description: str, resume_content: str, company_name: Optional[str] = None, job_title: Optional[str] = None) -> str:
        """Build prompt for interview preparation."""
        return f"""
You are an expert interview coach. Based on the job description and candidate's resume, generate comprehensive interview preparation materials.

Job Title: {job_title or 'Not specified'}
Company: {company_name or 'Not specified'}

Job Description:
{job_description}

Candidate Resume:
{resume_content[:2000]}  # Limit resume content to avoid token limits

Please provide a JSON response with the following structure:
{{
    "questions": [
        {{
            "question": "Tell me about yourself",
            "type": "behavioral",
            "suggested_answer": "Based on your resume, here's how to answer...",
            "tips": ["Focus on relevant experience", "Highlight achievements"]
        }}
    ],
    "technical_questions": [
        {{
            "question": "Technical question based on job requirements",
            "category": "programming",
            "difficulty": "medium",
            "suggested_approach": "How to approach this question"
        }}
    ],
    "preparation_tips": [
        "Research the company culture",
        "Prepare STAR method examples",
        "Review your resume thoroughly"
    ],
    "key_topics": ["Topic 1", "Topic 2"],
    "strengths_to_highlight": ["Strength 1", "Strength 2"],
    "weaknesses_to_address": ["Weakness 1", "Weakness 2"],
    "company_research": "Key points about the company",
    "questions_to_ask": [
        "What does success look like in this role?",
        "What are the team's biggest challenges?"
    ]
}}
"""
    
    def _parse_interview_prep_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response for interview preparation."""
        try:
            data = json.loads(content)
            return {
                "questions": data.get("questions", []),
                "technical_questions": data.get("technical_questions", []),
                "preparation_tips": data.get("preparation_tips", []),
                "key_topics": data.get("key_topics", []),
                "strengths_to_highlight": data.get("strengths_to_highlight", []),
                "weaknesses_to_address": data.get("weaknesses_to_address", []),
                "company_research": data.get("company_research", ""),
                "questions_to_ask": data.get("questions_to_ask", [])
            }
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse interview prep response as JSON. Using fallback.")
            return self._mock_interview_prep(None, None)
    
    def _mock_interview_prep(self, job_title: Optional[str] = None, company_name: Optional[str] = None) -> Dict[str, Any]:
        """Mock interview preparation response."""
        return {
            "questions": [
                {
                    "question": "Tell me about yourself",
                    "type": "behavioral",
                    "suggested_answer": "Focus on your relevant experience and achievements that align with this role.",
                    "tips": ["Be concise", "Highlight relevant experience", "Show enthusiasm"]
                },
                {
                    "question": "Why do you want to work here?",
                    "type": "motivational",
                    "suggested_answer": f"Express genuine interest in {company_name or 'the company'} and the role.",
                    "tips": ["Research the company", "Connect your values to theirs", "Be specific"]
                }
            ],
            "technical_questions": [
                {
                    "question": "Describe your experience with relevant technologies",
                    "category": "technical",
                    "difficulty": "medium",
                    "suggested_approach": "Provide specific examples from your resume"
                }
            ],
            "preparation_tips": [
                "Research the company thoroughly",
                "Review the job description and align your experience",
                "Prepare STAR method examples",
                "Practice common interview questions",
                "Prepare questions to ask the interviewer"
            ],
            "key_topics": ["Technical skills", "Problem-solving", "Team collaboration"],
            "strengths_to_highlight": ["Relevant experience", "Problem-solving skills"],
            "weaknesses_to_address": ["Areas for growth", "Learning opportunities"],
            "company_research": f"Research {company_name or 'the company'} culture, values, and recent news.",
            "questions_to_ask": [
                "What does success look like in this role?",
                "What are the team's biggest challenges?",
                "How does the company support professional development?"
            ]
        }

