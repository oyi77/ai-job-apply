"""G4F AI service implementation for the AI Job Application Assistant."""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from src.core.ai_service import AIService
from src.models.resume import (
    ResumeOptimizationRequest,
    ResumeOptimizationResponse,
    Resume,
)
from src.models.cover_letter import CoverLetterRequest, CoverLetter
from src.models.career_insights import CareerInsightsRequest, CareerInsightsResponse
from src.config import config
from loguru import logger


class G4FAIService(AIService):
    """Concrete implementation of AIService using G4F (free AI models)."""

    def __init__(self, db_session=None, api_key: str = None):
        """Initialize the G4F AI service.

        Args:
            db_session: Optional database session for dynamic config
            api_key: Optional API key (overrides config and database)
        """
        self.logger = logger.bind(module="G4FAIService")
        self.client = None
        self._db_session = db_session
        self._api_key_override = api_key

        # Configuration values
        self.api_key = None
        self.model_name = "gpt-4"  # G4F supports multiple models
        self.temperature = 0.7
        self.max_tokens = 2048

        # Usage tracking
        self.requests_today = 0
        self.cost_today = 0.0

        # Load configuration
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load configuration from database or environment."""
        # Priority: 1. Override, 2. Database, 3. Environment

        # Check for override
        if self._api_key_override:
            self.api_key = self._api_key_override
            self.logger.info("Using API key from constructor override")
            self._initialize_client()
            return

        # Try to load from database
        if self._db_session:
            try:
                from sqlalchemy import select
                from src.database.models import AIProviderConfig

                result = asyncio.run(
                    self._db_session.execute(
                        select(AIProviderConfig).where(
                            AIProviderConfig.provider_name == "g4f"
                        )
                    )
                )
                db_config = result.scalar_one_or_none()

                if db_config and db_config.is_enabled and db_config.api_key_encrypted:
                    self.api_key = db_config.api_key_encrypted
                    self.model_name = db_config.default_model or self.model_name
                    self.temperature = db_config.temperature
                    self.max_tokens = db_config.max_tokens
                    self.logger.info(
                        f"Loaded G4F config from database: model={self.model_name}"
                    )
                    self._initialize_client()
                    return
                elif db_config:
                    self.logger.info("G4F provider found in DB but not enabled")
            except Exception as e:
                self.logger.warning(f"Could not load AI config from database: {e}")

        # Fallback to environment
        self.api_key = config.openai_api_key or "g4f"  # G4F doesn't require API key
        self.logger.info("Using G4F with free models (no API key required)")

        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the G4F client."""
        try:
            import g4f

            self.client = g4f.client.Client()
            self.logger.info(
                f"G4F AI service initialized with model: {self.model_name}"
            )
        except ImportError:
            self.logger.error(
                "G4F library not installed. Install with: pip install g4f"
            )
            self.client = None
        except Exception as e:
            self.logger.error(f"Failed to initialize G4F AI service: {e}")
            self.client = None

    async def optimize_resume(
        self, request: ResumeOptimizationRequest
    ) -> ResumeOptimizationResponse:
        """Optimize resume for a specific job using G4F AI."""
        try:
            self.logger.info(
                f"Optimizing resume for {request.target_role} at {request.company_name}"
            )

            if not await self.is_available():
                return self._mock_resume_optimization(request)

            # Create the optimization prompt
            prompt = self._build_resume_optimization_prompt(request)

            # Generate response using G4F
            response = await self._generate_content(prompt)

            if response:
                # Parse the AI response
                optimization_data = self._parse_resume_optimization_response(response)

                # Create resume object
                original_resume = Resume(
                    name="Current Resume",
                    file_path=f"./resumes/{request.resume_id}.pdf",
                    file_type="pdf",
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
                    ats_recommendations=optimization_data.get("ats_recommendations"),
                )
            else:
                return self._mock_resume_optimization(request)

        except Exception as e:
            self.logger.error(f"Error optimizing resume: {e}", exc_info=True)
            return self._mock_resume_optimization(request)

    async def generate_cover_letter(self, request: CoverLetterRequest) -> CoverLetter:
        """Generate a personalized cover letter using G4F AI."""
        try:
            self.logger.info(
                f"Generating cover letter for {request.job_title} at {request.company_name}"
            )

            if not await self.is_available():
                return self._mock_cover_letter_generation(request)

            # Create the cover letter prompt
            prompt = self._build_cover_letter_prompt(request)

            # Generate response using G4F
            response = await self._generate_content(prompt)

            if response:
                # Parse the AI response
                cover_letter_data = self._parse_cover_letter_response(response)

                return CoverLetter(
                    job_title=request.job_title,
                    company_name=request.company_name,
                    content=cover_letter_data.get("content", ""),
                    tone=request.tone,
                    word_count=len(cover_letter_data.get("content", "").split()),
                )
            else:
                return self._mock_cover_letter_generation(request)

        except Exception as e:
            self.logger.error(f"Error generating cover letter: {e}", exc_info=True)
            return self._mock_cover_letter_generation(request)

    async def analyze_job_match(
        self, resume_content: str, job_description: str
    ) -> Dict[str, Any]:
        """Analyze how well a resume matches a job description using G4F AI."""
        try:
            self.logger.info("Analyzing job match using G4F AI")

            if not await self.is_available():
                return self._mock_job_match_analysis()

            # Create the job match analysis prompt
            prompt = self._create_job_match_prompt(resume_content, job_description)

            # Generate response using G4F
            response = await self._generate_content(prompt)

            if response:
                return self._parse_job_match_response(response)
            else:
                return self._mock_job_match_analysis()

        except Exception as e:
            self.logger.error(f"Error analyzing job match: {e}", exc_info=True)
            return self._mock_job_match_analysis()

    async def extract_resume_skills(self, resume_content: str) -> List[str]:
        """Extract skills from resume content using G4F AI."""
        try:
            self.logger.info("Extracting skills from resume using G4F AI")

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

            # Generate response using G4F
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

    async def suggest_resume_improvements(
        self, resume_content: str, job_description: str
    ) -> List[str]:
        """Suggest improvements for a resume based on job description using G4F AI."""
        try:
            self.logger.info("Generating resume improvement suggestions using G4F AI")

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

            # Generate response using G4F
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
            self.logger.error(
                f"Error generating improvement suggestions: {e}", exc_info=True
            )
            return self._mock_improvement_suggestions()

    async def prepare_interview(
        self,
        job_description: str,
        resume_content: str,
        company_name: Optional[str] = None,
        job_title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Prepare interview questions and tips based on job description and resume."""
        try:
            self.logger.info(
                f"Preparing interview questions for {job_title} at {company_name}"
            )

            # Build prompt for interview preparation
            prompt = self._build_interview_prep_prompt(
                job_description, resume_content, company_name, job_title
            )

            # Generate content using G4F
            content = await self._generate_content(prompt)

            if content:
                return self._parse_interview_prep_response(content)
            else:
                return self._mock_interview_prep(job_title, company_name)

        except Exception as e:
            self.logger.error(f"Error preparing interview: {e}", exc_info=True)
            return self._mock_interview_prep(job_title, company_name)

    def _build_interview_prep_prompt(
        self,
        job_description: str,
        resume_content: str,
        company_name: Optional[str] = None,
        job_title: Optional[str] = None,
    ) -> str:
        """Build prompt for interview preparation."""
        return f"""
You are an expert interview coach. Based on the job description and candidate's resume, generate comprehensive interview preparation materials.

Job Title: {job_title or "Not specified"}
Company: {company_name or "Not specified"}

Job Description:
{job_description}

Candidate Resume:
{resume_content[:2000]}

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

    def _parse_interview_prep_response(self, response: str) -> Dict[str, Any]:
        """Parse the interview preparation response from G4F."""
        try:
            data = json.loads(response)
            return {
                "questions": data.get("questions", []),
                "technical_questions": data.get("technical_questions", []),
                "preparation_tips": data.get("preparation_tips", []),
                "key_topics": data.get("key_topics", []),
                "strengths_to_highlight": data.get("strengths_to_highlight", []),
                "weaknesses_to_address": data.get("weaknesses_to_address", []),
                "company_research": data.get("company_research", ""),
                "questions_to_ask": data.get("questions_to_ask", []),
            }
        except json.JSONDecodeError:
            self.logger.warning(
                "Failed to parse G4F interview prep response as JSON. Using fallback."
            )
            return self._mock_interview_prep(None, None)

    def _mock_interview_prep(
        self, job_title: Optional[str] = None, company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock interview preparation response."""
        return {
            "questions": [
                {
                    "question": "Tell me about yourself",
                    "type": "behavioral",
                    "suggested_answer": "Focus on your relevant experience and achievements that align with this role.",
                    "tips": [
                        "Be concise",
                        "Highlight relevant experience",
                        "Show enthusiasm",
                    ],
                },
                {
                    "question": "Why do you want to work here?",
                    "type": "motivational",
                    "suggested_answer": f"Express genuine interest in {company_name or 'the company'} and the role.",
                    "tips": [
                        "Research the company",
                        "Connect your values to theirs",
                        "Be specific",
                    ],
                },
            ],
            "technical_questions": [
                {
                    "question": "Describe your experience with relevant technologies",
                    "category": "technical",
                    "difficulty": "medium",
                    "suggested_approach": "Provide specific examples from your resume",
                }
            ],
            "preparation_tips": [
                "Research the company thoroughly",
                "Review the job description and align your experience",
                "Prepare STAR method examples",
                "Practice common interview questions",
                "Prepare questions to ask the interviewer",
            ],
            "key_topics": ["Technical skills", "Problem-solving", "Team collaboration"],
            "strengths_to_highlight": ["Relevant experience", "Problem-solving skills"],
            "weaknesses_to_address": ["Areas for growth", "Learning opportunities"],
            "company_research": f"Research {company_name or 'the company'} culture, values, and recent news.",
            "questions_to_ask": [
                "What does success look like in this role?",
                "What are the team's biggest challenges?",
                "How does the company support professional development?",
            ],
        }

    async def is_available(self) -> bool:
        """Check if the G4F AI service is available."""
        return self.client is not None

    async def _generate_content(self, prompt: str) -> Optional[str]:
        """Generate content using G4F AI."""
        try:
            if not self.client:
                return None

            # G4F client is synchronous, so we run it in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._sync_generate_content,
                prompt,
            )
            return response

        except Exception as e:
            self.logger.error(f"Error generating content with G4F: {e}", exc_info=True)
            return None

    def _sync_generate_content(self, prompt: str) -> Optional[str]:
        """Synchronous wrapper for G4F content generation."""
        try:
            if not self.client:
                return None

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Extract text from response
            if hasattr(response, "choices") and response.choices:
                return response.choices[0].message.content
            return None

        except Exception as e:
            self.logger.error(f"Error in sync G4F generation: {e}", exc_info=True)
            return None

    def _build_resume_optimization_prompt(
        self, request: ResumeOptimizationRequest
    ) -> str:
        """Create a prompt for ATS-optimized resume optimization."""
        # Safely access resume_content using getattr to avoid AttributeError
        resume_content = getattr(request, "resume_content", None)
        resume_content_str = resume_content[:3000] if resume_content else "Not provided"

        return f"""
        You are an expert resume optimizer specializing in ATS (Applicant Tracking System) optimization. 
        Optimize the following resume for the target role and company, ensuring maximum ATS compatibility.
        
        Target Role: {request.target_role}
        Company: {request.company_name or "Not specified"}
        Job Description: {request.job_description}
        Resume Content: {resume_content_str}
        
        Please provide a JSON response with the following structure:
        {{
            "optimized_content": "The ATS-optimized resume content",
            "suggestions": ["suggestion1", "suggestion2"],
            "skill_gaps": ["missing_skill1", "missing_skill2"],
            "improvements": ["improvement1", "improvement2"],
            "ats_score": 0.85,
            "ats_checks": {{
                "keyword_match": 0.90,
                "formatting": 0.85,
                "section_structure": 0.80,
                "contact_info": 0.95
            }},
            "ats_recommendations": [
                "Use standard section headers (Work Experience, Education, Skills)",
                "Include job description keywords naturally throughout",
                "Use simple formatting without tables or graphics",
                "Ensure all text is selectable (not in images)"
            ],
            "confidence_score": 0.85
        }}
        
        ATS Optimization Requirements:
        1. KEYWORD OPTIMIZATION:
           - Extract key terms, skills, and qualifications from the job description
           - Naturally integrate these keywords throughout the resume
           - Match job title variations (e.g., "Software Engineer" vs "Developer")
           - Include industry-specific terminology
        
        2. FORMATTING & STRUCTURE:
           - Use standard section headers: "Work Experience", "Education", "Skills", "Summary"
           - Avoid complex layouts, tables, graphics, or images
           - Use simple, clean formatting with clear hierarchy
           - Ensure all text is machine-readable (not scanned images)
           - Use standard fonts (Arial, Calibri, Times New Roman)
           - Maintain consistent date formats (MM/YYYY or Month YYYY)
        
        3. CONTENT OPTIMIZATION:
           - Use bullet points for achievements and responsibilities
           - Include quantifiable metrics and achievements
           - Use action verbs (developed, implemented, managed, etc.)
           - Match experience descriptions to job requirements
           - Highlight relevant skills prominently
        
        4. CONTACT INFORMATION:
           - Ensure contact info is clearly formatted at the top
           - Include: Name, Phone, Email, LinkedIn (optional), Location (City, State)
           - Use standard formats (no special characters that break parsing)
        
        5. SKILLS SECTION:
           - List technical skills clearly
           - Match skills to job description requirements
           - Include proficiency levels if relevant
           - Use standard skill names (avoid abbreviations unless common)
        
        Focus on making the resume:
        - ATS-friendly (will parse correctly in applicant tracking systems)
        - Keyword-optimized (matches job description requirements)
        - Professionally formatted (clean, readable, standard structure)
        - Achievement-focused (quantifiable results and impact)
        - Role-specific (tailored to the target position)
        """

    def _build_cover_letter_prompt(self, request: CoverLetterRequest) -> str:
        """Create a prompt for cover letter generation."""
        return f"""
        You are an expert cover letter writer. Generate a personalized cover letter for the following job application.
        
        Job Title: {request.job_title}
        Company: {request.company_name}
        Job Description: {request.job_description}
        Resume Summary: {request.resume_summary}
        Tone: {request.tone}
        Focus Areas: {", ".join(request.focus_areas or [])}
        Custom Instructions: {request.custom_instructions or "None"}
        
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

    def _create_job_match_prompt(
        self, resume_content: str, job_description: str
    ) -> str:
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
        """Parse the resume optimization response from G4F."""
        try:
            data = json.loads(response)
            return {
                "optimized_content": data.get(
                    "optimized_content", response[:500] + "..."
                ),
                "suggestions": data.get("suggestions", []),
                "skill_gaps": data.get("skill_gaps", []),
                "improvements": data.get("improvements", []),
                "confidence_score": data.get("confidence_score", 0.75),
                "ats_score": data.get("ats_score"),
                "ats_checks": data.get("ats_checks"),
                "ats_recommendations": data.get("ats_recommendations", []),
            }
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            return {
                "optimized_content": response[:500] + "...",
                "suggestions": ["Add more specific achievements", "Improve formatting"],
                "skill_gaps": ["Technical skills", "Certifications"],
                "improvements": ["Enhanced content", "Better structure"],
                "confidence_score": 0.75,
                "ats_score": 0.70,
                "ats_checks": {
                    "keyword_match": 0.65,
                    "formatting": 0.70,
                    "section_structure": 0.75,
                    "contact_info": 0.80,
                },
                "ats_recommendations": [
                    "Use standard section headers",
                    "Include job description keywords",
                    "Simplify formatting",
                ],
            }

    def _parse_cover_letter_response(self, response: str) -> Dict[str, Any]:
        """Parse the cover letter response from G4F."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {"content": response}

    def _parse_job_match_response(self, response: str) -> Dict[str, Any]:
        """Parse the job match analysis response from G4F."""
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
                    "skills_score": 0.5,
                },
                "experience_match": {
                    "required_years": 3,
                    "candidate_years": 2,
                    "experience_score": 0.67,
                },
                "recommendations": [
                    "Highlight relevant projects",
                    "Add missing skills",
                ],
                "confidence": 0.7,
            }

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text response."""
        # Simple skill extraction fallback
        common_skills = [
            "Python",
            "JavaScript",
            "Java",
            "React",
            "Node.js",
            "SQL",
            "Git",
            "Docker",
            "AWS",
            "Machine Learning",
            "Data Analysis",
        ]
        return [skill for skill in common_skills if skill.lower() in text.lower()]

    def _extract_suggestions_from_text(self, text: str) -> List[str]:
        """Extract suggestions from text response."""
        import re

        # Simple suggestion extraction fallback
        lines = text.split("\n")
        suggestions = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Match bullets (- • *) or numbered lists (1. 2.)
            if re.match(r"^[-•*\d.]+\s+", line):
                # Clean up the prefix
                cleaned = re.sub(r"^[-•*\d.]+\s+", "", line)
                if cleaned:
                    suggestions.append(cleaned)

        return suggestions[:5]  # Limit to 5 suggestions

    # Mock methods for fallback functionality
    def _mock_resume_optimization(
        self, request: ResumeOptimizationRequest
    ) -> ResumeOptimizationResponse:
        """Mock resume optimization response."""
        original_resume = Resume(
            name="Current Resume",
            file_path=f"./resumes/{request.resume_id}.pdf",
            file_type="pdf",
        )

        return ResumeOptimizationResponse(
            original_resume=original_resume,
            optimized_content=f"Optimized resume for {request.target_role} position...",
            suggestions=[
                "Add more specific technical skills",
                "Include quantifiable achievements",
                "Tailor experience descriptions to match job requirements",
            ],
            skill_gaps=["Cloud computing", "Machine learning"],
            improvements=[
                "Enhanced technical skills section",
                "Added project-based achievements",
                "Improved formatting and readability",
            ],
            confidence_score=0.85,
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
            word_count=len(content.split()),
        )

    def _mock_job_match_analysis(self) -> Dict[str, Any]:
        """Mock job match analysis response."""
        return {
            "overall_match_score": 0.78,
            "skills_match": {
                "required_skills": ["Python", "JavaScript", "React"],
                "matching_skills": ["Python", "JavaScript"],
                "missing_skills": ["React"],
                "skills_score": 0.67,
            },
            "experience_match": {
                "required_years": 3,
                "candidate_years": 4,
                "experience_score": 0.85,
            },
            "recommendations": [
                "Highlight React experience if available",
                "Emphasize project-based achievements",
                "Include specific technical accomplishments",
            ],
            "confidence": 0.82,
        }

    def _mock_skills_extraction(self) -> List[str]:
        """Mock skills extraction response."""
        return [
            "Python",
            "JavaScript",
            "SQL",
            "Git",
            "Docker",
            "AWS",
            "React",
            "Node.js",
        ]

    def _mock_improvement_suggestions(self) -> List[str]:
        """Mock improvement suggestions response."""
        return [
            "Add specific metrics for project achievements",
            "Include relevant certifications",
            "Highlight leadership experience",
            "Use consistent bullet point formatting",
            "Add industry-specific keywords",
        ]
