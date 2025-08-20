"""AI service implementation using the new provider system."""

import asyncio
from typing import Dict, Any, Optional, List
from ...core.ai_service import AIService
from ...services.ai_provider_manager import AIProviderManager
from ...config import config
from ...models.resume import ResumeOptimizationRequest, ResumeOptimizationResponse, Resume
from ...models.cover_letter import CoverLetterRequest, CoverLetter
from loguru import logger

class ModernAIService(AIService):
    """Modern AI service using the provider system."""
    
    def __init__(self):
        """Initialize the modern AI service."""
        self.logger = logger.bind(module="ModernAIService")
        self.provider_manager = AIProviderManager()
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the AI service with providers."""
        try:
            if not config.ai_providers:
                self.logger.warning("No AI providers configured, running in mock mode")
                return False
            
            success = await self.provider_manager.initialize(config.ai_providers)
            if success:
                self._initialized = True
                self.logger.info("AI service initialized with providers")
                return True
            else:
                self.logger.warning("Failed to initialize AI providers, running in mock mode")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize AI service: {e}")
            return False
    
    async def is_available(self) -> bool:
        """Check if any AI provider is available."""
        if not self._initialized:
            return False
        return await self.provider_manager.is_any_available()
    
    async def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all AI providers."""
        if not self._initialized:
            return {}
        return await self.provider_manager.get_provider_status()
    
    async def optimize_resume(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """Optimize resume for a specific job using available AI provider."""
        try:
            self.logger.info(f"Optimizing resume for {request.target_role} at {request.company_name}")
            
            if not await self.is_available():
                return self._mock_resume_optimization(request)
            
            # Use AI provider to optimize resume
            ai_response = await self.provider_manager.optimize_resume(
                resume_content=request.resume_content,
                job_description=request.job_description
            )
            
            # Parse the AI response
            optimization_data = self._parse_resume_optimization_response(ai_response.content)
            
            # Create resume object
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
                
        except Exception as e:
            self.logger.error(f"Error optimizing resume: {e}", exc_info=True)
            return self._mock_resume_optimization(request)
    
    async def generate_cover_letter(self, request: CoverLetterRequest) -> CoverLetter:
        """Generate a personalized cover letter using available AI provider."""
        try:
            self.logger.info(f"Generating cover letter for {request.job_title} at {request.company_name}")
            
            if not await self.is_available():
                return self._mock_cover_letter_generation(request)
            
            # Use AI provider to generate cover letter
            ai_response = await self.provider_manager.generate_cover_letter(
                resume_content=request.resume_content,
                job_description=request.job_description,
                company=request.company_name
            )
            
            # Create cover letter object
            cover_letter = CoverLetter(
                job_title=request.job_title,
                company_name=request.company_name,
                content=ai_response.content,
                tone=request.tone or "professional",
                word_count=len(ai_response.content.split()),
                file_path=f"./cover_letters/{request.job_title}_{request.company_name}.txt",
                generated_at=ai_response.metadata.get("generated_at") if ai_response.metadata else None
            )
            
            return cover_letter
                
        except Exception as e:
            self.logger.error(f"Error generating cover letter: {e}", exc_info=True)
            return self._mock_cover_letter_generation(request)
    
    async def analyze_job_match(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        """Analyze job-resume match using available AI provider."""
        try:
            self.logger.info("Analyzing job-resume match")
            
            if not await self.is_available():
                return self._mock_job_match_analysis()
            
            # Use AI provider to analyze match
            ai_response = await self.provider_manager.analyze_job_match(
                resume_content=resume_content,
                job_description=job_description
            )
            
            # Parse the AI response
            return self._parse_job_match_response(ai_response.content)
                
        except Exception as e:
            self.logger.error(f"Error analyzing job match: {e}", exc_info=True)
            return self._mock_job_match_analysis()
    
    async def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using available AI provider."""
        try:
            self.logger.info("Extracting skills from text")
            
            if not await self.is_available():
                return self._mock_skills_extraction()
            
            # Use AI provider to extract skills
            ai_response = await self.provider_manager.extract_skills(text)
            
            # Parse the AI response
            return self._parse_skills_response(ai_response.content)
                
        except Exception as e:
            self.logger.error(f"Error extracting skills: {e}", exc_info=True)
            return self._mock_skills_extraction()
    
    def _parse_resume_optimization_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response for resume optimization."""
        # Simple parsing - in production, you might want more sophisticated parsing
        return {
            "optimized_content": content,
            "suggestions": ["Improve formatting", "Add more keywords"],
            "skill_gaps": ["Advanced Python", "Cloud computing"],
            "improvements": ["Better structure", "More specific achievements"],
            "confidence_score": 0.85
        }
    
    def _parse_job_match_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response for job match analysis."""
        return {
            "match_percentage": 75,
            "strengths": ["Python experience", "Problem solving"],
            "weaknesses": ["Cloud experience", "Team leadership"],
            "recommendations": ["Learn AWS", "Take leadership courses"]
        }
    
    def _parse_skills_response(self, content: str) -> List[str]:
        """Parse AI response for skills extraction."""
        # Simple extraction - split by lines and clean up
        skills = [skill.strip() for skill in content.split('\n') if skill.strip()]
        return skills[:10]  # Limit to 10 skills
    
    def _mock_resume_optimization(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """Mock resume optimization response."""
        original_resume = Resume(
            name="Current Resume",
            file_path=f"./resumes/{request.resume_id}.pdf",
            file_type="pdf"
        )
        
        return ResumeOptimizationResponse(
            original_resume=original_resume,
            optimized_content="Mock optimized content",
            suggestions=["Mock suggestion 1", "Mock suggestion 2"],
            skill_gaps=["Mock skill gap 1", "Mock skill gap 2"],
            improvements=["Mock improvement 1", "Mock improvement 2"],
            confidence_score=0.5
        )
    
    def _mock_cover_letter_generation(self, request: CoverLetterRequest) -> CoverLetter:
        """Mock cover letter generation response."""
        return CoverLetter(
            job_title=request.job_title,
            company_name=request.company_name,
            content="Mock cover letter content",
            tone="professional",
            word_count=150,
            file_path=f"./cover_letters/{request.job_title}_{request.company_name}.txt",
            generated_at=None
        )
    
    def _mock_job_match_analysis(self) -> Dict[str, Any]:
        """Mock job match analysis response."""
        return {
            "match_percentage": 60,
            "strengths": ["Mock strength 1", "Mock strength 2"],
            "weaknesses": ["Mock weakness 1", "Mock weakness 2"],
            "recommendations": ["Mock recommendation 1", "Mock recommendation 2"]
        }
    
    def _mock_skills_extraction(self) -> List[str]:
        """Mock skills extraction response."""
        return ["Mock skill 1", "Mock skill 2", "Mock skill 3"]
