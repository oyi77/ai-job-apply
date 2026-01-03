"""Local AI provider implementation for OpenLLaMA and similar models."""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from src.core.ai_provider import AIProvider, AIProviderConfig, AIResponse
from loguru import logger

class LocalAIProvider(AIProvider):
    """Local AI provider implementation for OpenLLaMA, LLMStudio, etc."""
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self._available = False
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self) -> bool:
        """Initialize local AI provider."""
        try:
            if not self.config.base_url:
                logger.warning("Local AI base URL not provided")
                return False
            
            # Test connection
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/health", timeout=5) as response:
                    if response.status == 200:
                        self._available = True
                        logger.info(f"Local AI provider at {self.config.base_url} initialized successfully")
                        return True
            
            self._available = False
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize local AI provider: {e}")
            self._available = False
            return False
    
    async def is_available(self) -> bool:
        """Check if local AI is available."""
        return self._available
    
    async def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to local AI endpoint."""
        if not await self.is_available():
            raise RuntimeError("Local AI provider not available")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.base_url}{endpoint}",
                    json=payload,
                    timeout=self.config.timeout
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Local AI request failed with status {response.status}")
                    
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Local AI request failed: {e}")
            raise RuntimeError(f"Local AI request failed: {e}")
    
    async def generate_text(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text using local AI."""
        payload = {
            "prompt": prompt,
            "model": self.config.model,
            "temperature": kwargs.get('temperature', self.config.temperature),
            "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
            "stream": False
        }
        
        try:
            response = await self._make_request("/v1/completions", payload)
            
            content = response.get("choices", [{}])[0].get("text", "")
            
            return AIResponse(
                content=content,
                provider="local_ai",
                model=self.config.model,
                usage=response.get("usage"),
                metadata={
                    "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
                    "response_id": response.get("id")
                }
            )
            
        except Exception as e:
            logger.error(f"Local AI text generation failed: {e}")
            raise RuntimeError(f"Local AI text generation failed: {e}")
    
    async def optimize_resume(self, resume_content: str, job_description: str) -> AIResponse:
        """Optimize resume for a specific job."""
        prompt = f"""
        Please optimize the following resume for the job description below.
        
        Resume:
        {resume_content}
        
        Job Description:
        {job_description}
        
        Please provide:
        1. An optimized version of the resume
        2. Specific improvements made
        3. Keywords and skills to highlight
        4. Formatting suggestions
        
        Focus on making the resume more relevant to this specific job.
        """
        
        return await self.generate_text(prompt)
    
    async def generate_cover_letter(self, resume_content: str, job_description: str, company: str) -> AIResponse:
        """Generate a cover letter."""
        prompt = f"""
        Please generate a professional cover letter based on the following information:
        
        Resume:
        {resume_content}
        
        Job Description:
        {job_description}
        
        Company: {company}
        
        The cover letter should:
        1. Be professional and engaging
        2. Highlight relevant experience from the resume
        3. Show enthusiasm for the company and role
        4. Be 250-400 words
        5. Include a clear call to action
        
        Format as a proper business letter.
        """
        
        return await self.generate_text(prompt)
    
    async def analyze_job_match(self, resume_content: str, job_description: str) -> AIResponse:
        """Analyze job-resume match."""
        prompt = f"""
        Please analyze the match between this resume and job description:
        
        Resume:
        {resume_content}
        
        Job Description:
        {job_description}
        
        Please provide:
        1. Match percentage (0-100%)
        2. Key strengths that align
        3. Areas for improvement
        4. Missing skills or experience
        5. Recommendations to improve the match
        
        Be specific and actionable in your analysis.
        """
        
        return await self.generate_text(prompt)
    
    async def extract_skills(self, text: str) -> AIResponse:
        """Extract skills from text."""
        prompt = f"""
        Please extract and categorize skills from the following text:
        
        Text:
        {text}
        
        Please provide:
        1. Technical skills (programming languages, tools, technologies)
        2. Soft skills (communication, leadership, problem-solving)
        3. Industry-specific skills
        4. Certifications mentioned
        5. Experience levels for each skill (beginner, intermediate, expert)
        
        Format as a structured list with clear categories.
        """
        
        return await self.generate_text(prompt)
