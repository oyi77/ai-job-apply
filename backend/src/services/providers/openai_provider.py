"""OpenAI provider implementation."""

import asyncio
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from src.core.ai_provider import AIProvider, AIProviderConfig, AIResponse
from loguru import logger

class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.client: Optional[AsyncOpenAI] = None
        self._available = False
    
    async def initialize(self) -> bool:
        """Initialize OpenAI client."""
        try:
            if not self.config.api_key:
                logger.warning("OpenAI API key not provided")
                return False
            
            self.client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
            
            # Test connection
            await self.client.models.list()
            self._available = True
            logger.info("OpenAI provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            self._available = False
            return False
    
    async def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self._available and self.client is not None
    
    async def generate_text(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text using OpenAI."""
        if not await self.is_available():
            raise RuntimeError("OpenAI provider not available")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                timeout=kwargs.get('timeout', self.config.timeout)
            )
            
            content = response.choices[0].message.content or ""
            
            return AIResponse(
                content=content,
                provider="openai",
                model=self.config.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI text generation failed: {e}")
            raise RuntimeError(f"OpenAI text generation failed: {e}")
    
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
