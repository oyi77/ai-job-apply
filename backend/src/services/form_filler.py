"""Form Filler Service.

Service for filling job application forms using YAML templates and AI fallback.
Supports LinkedIn, Indeed, and Glassdoor platforms with intelligent field population.
"""

from typing import Optional, Dict, List
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.ai_service import AIService
from src.utils.logger import get_logger
from src.models.job import Job
from src.models.application import JobApplication, ApplicationStatus


class FormFillerService:
    """Service for filling job application forms using YAML templates.

    Implements:
    - YAML template loading from configuration files
    - Form field iteration and value application
    - Mapped answer lookup from YAML
    - AI fallback for unknown/custom fields
    - Error handling and logging for form filling failures
    """

    def __init__(self, ai_service: AIService, user_id: str):
        """Initialize form filler service.

        Args:
            ai_service: AI service for generating responses
            user_id: User ID for tracking
        """
        self.ai_service = ai_service
        self.user_id = user_id
        self.logger = get_logger(__name__)

        # Load form templates from YAML
        self.templates = self._load_form_templates()

        self.logger.info(
            f"FormFiller initialized for user {user_id} "
            f"with {len(self.templates.get('linkedin', {}))} LinkedIn, "
            f"{len(self.templates.get('indeed', {}))} Indeed, "
            f"{len(self.templates.get('glassdoor', {}))} Glassdoor fields"
        )

    def _load_form_templates(self) -> Dict[str, Dict]:
        """Load form field templates from YAML configuration file.

        Returns:
            Dictionary with field definitions for each platform
            Format: {platform: {field_name: field_definition}}
        """
        try:
            import yaml

            # Path to YAML file
            yaml_path = (
                Path(__file__).parent / "config" / "application_form_fields.yaml"
            )

            if not yaml_path.exists():
                self.logger.warning(f"YAML file not found at {yaml_path}")
                return {}

            with open(yaml_path, "r") as f:
                templates = yaml.safe_load(f)

            self.logger.info(f"Loaded {len(templates)} platform sections from YAML")
            return templates

        except yaml.YAMLError as e:
            self.logger.error(f"YAML parsing error: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading form templates: {e}")
            return {}

    async def fill_form(
        self,
        platform: str,
        field_values: Dict[str, str],
        user_preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Fill a form using templates and AI fallback.

        Args:
            platform: Platform name (linkedin, indeed, glassdoor)
            field_values: Dictionary of field names to values
            user_preferences: Optional user-provided answers for fields

        Returns:
            Dictionary with field name to filled value
            Format: {field_name: field_value}
        """
        try:
            # Get platform templates
            platform_templates = self.templates.get(platform, {})

            if not platform_templates:
                self.logger.warning(f"No form templates found for platform: {platform}")
                return {}

            filled_fields = {}

            # Iterate through each field definition
            for field_name, field_def in platform_templates.items():
                # Get field type and attributes
                field_type = field_def.get("type")
                xpath = field_def.get("xpath")
                ai_fallback = field_def.get("ai_fallback", False)

                # Determine field value
                value = await self._get_field_value(
                    field_name=field_name,
                    field_def=field_def,
                    field_values=field_values,
                    user_preferences=user_preferences,
                )

                if value:
                    filled_fields[field_name] = value
                    self.logger.debug(
                        f"Filled field {field_name} with value: {str(value)[:100]}..."
                    )

            return filled_fields

        except Exception as e:
            self.logger.error(f"Error filling form for {platform}: {e}")
            return {}

    async def _get_field_value(
        self,
        field_name: str,
        field_def: Dict[str, str],
        field_values: Dict[str, str],
        user_preferences: Optional[Dict[str, str]],
    ) -> Optional[str]:
        """Get value for a specific field using templates, user prefs, or AI.

        Args:
            field_name: Name of the field (e.g., "years_of_experience")
            field_def: Field definition from YAML
            field_values: User-provided values
            user_preferences: Optional user preference overrides

        Returns:
            Field value (string for text/select/checkbox, number for numeric fields)
        """
        # Check user preferences first
        if user_preferences and field_name in user_preferences:
            # User provided explicit answer
            return user_preferences[field_name]

        # Check if user provided value in field_values
        if field_values and field_name in field_values:
            return field_values[field_name]

        # Check for mapped answers in YAML
        mapped_answers = field_def.get("answers", [])
        if mapped_answers and any(mapped_answers):
            # Use first non-empty mapped answer
            for answer in mapped_answers:
                if answer and str(answer).strip():
                    return answer

        # Check if AI fallback is enabled
        if field_def.get("ai_fallback"):
            # Generate AI response for custom/unknown fields
            value = await self._generate_ai_answer(field_name, field_def)
            return value

        # Use default value from YAML
        return field_def.get("default_value")

    async def _generate_ai_answer(
        self,
        field_name: str,
        field_def: Dict[str, str],
    ) -> Optional[str]:
        """Generate AI answer for a form field.

        Args:
            field_name: Name of the field (e.g., "skills_required")
            field_def: Field definition from YAML

        Returns:
            Generated answer from AI service
        """
        try:
            # Get field description for context
            description = field_def.get("description", f"Answer: {field_name}")

            # Create AI prompt
            prompt = f"""
            Provide a concise answer for the job application form field '{field_name}'.

            Context: Job application on a job portal
            Field Description: {description}

            Requirements:
            - Answer should be relevant and professional
            - Answer should match the job requirements
            - Answer should be concise (1-2 sentences for most fields)
            - For technical fields, include specific keywords or numbers

            Field Type: {field_def.get("type")}

            Please provide just the answer, no additional explanation.
            """

            # Call AI service
            response = await self.ai_service.generate_content(prompt)

            # Extract answer from response
            if response and hasattr(response, "parts"):
                # Gemini API returns parts (streaming or multi-part)
                # Get first part with text
                for part in response.parts:
                    if hasattr(part, "text"):
                        answer = part.text.strip()
                        if answer:
                            self.logger.info(f"Generated AI answer for {field_name}")
                            return answer
                        break

            # Fallback: Return None if AI fails
            if not answer:
                self.logger.warning(f"AI generation failed for field {field_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error generating AI answer for {field_name}: {e}")
            return None

    async def _fill_select_field(
        self,
        field_name: str,
        value: str,
        field_def: Dict[str, str],
    ) -> Dict[str, str]:
        """Fill a select dropdown field.

        Args:
            field_name: Name of the field
            value: Selected value for dropdown
            field_def: Field definition from YAML

        Returns:
            Dictionary with field operations
        """
        # Select the option
        selected_option = value

        # Validate against mapped answers
        mapped_answers = field_def.get("answers", [])
        if mapped_answers and selected_option not in mapped_answers:
            self.logger.warning(
                f"Selected value '{selected_option}' not in mapped answers for {field_name}"
            )

        return {
            "action": "select_option",
            "field_name": field_name,
            "selected_value": selected_option,
            "xpath": field_def.get("xpath"),
        }

    async def _fill_text_field(
        self,
        field_name: str,
        value: str,
        field_def: Dict[str, str],
    ) -> Dict[str, str]:
        """Fill a text input field.

        Args:
            field_name: Name of the field
            value: Text value to enter
            field_def: Field definition from YAML

        Returns:
            Dictionary with field operations
        """
        return {
            "action": "type_text",
            "field_name": field_name,
            "value": value,
            "xpath": field_def.get("xpath"),
        }

    async def _fill_textarea_field(
        self,
        field_name: str,
        value: str,
        field_def: Dict[str, str],
    ) -> Dict[str, str]:
        """Fill a textarea field.

        Args:
            field_name: Name of the field
            value: Text content to enter
            field_def: Field definition from YAML

        Returns:
            Dictionary with field operations
        """
        return {
            "action": "type_text",
            "field_name": field_name,
            "value": value,
            "xpath": field_def.get("xpath"),
        }

    async def _fill_number_field(
        self,
        field_name: str,
        value: int,
        field_def: Dict[str, str],
    ) -> Dict[str, str]:
        """Fill a numeric input field.

        Args:
            field_name: Name of the field
            value: Numeric value to enter
            field_def: Field definition from YAML

        Returns:
            Dictionary with field operations
        """
        return {
            "action": "type_number",
            "field_name": field_name,
            "value": value,
            "xpath": field_def.get("xpath"),
        }

    async def _fill_checkbox_field(
        self,
        field_name: str,
        value: bool,
        field_def: Dict[str, str],
    ) -> Dict[str, str]:
        """Fill a checkbox field.

        Args:
            field_name: Name of the field
            value: Boolean value (true/false)
            field_def: Field definition from YAML

        Returns:
            Dictionary with field operations
        """
        # Convert boolean to checkbox action
        if value:
            action = "check"
        else:
            action = "uncheck"

        return {
            "action": action,
            "field_name": field_name,
            "xpath": field_def.get("xpath"),
        }

    async def _fill_file_upload_field(
        self,
        field_name: str,
        file_data: bytes,
        file_name: str,
        content_type: str,
        field_def: Dict[str, str],
    ) -> Dict[str, str]:
        """Fill a file upload field.

        Args:
            field_name: Name of the field
            file_data: File content as bytes
            file_name: Name of the file (e.g., "resume.pdf")
            content_type: MIME type of the file (e.g., "application/pdf")
            field_def: Field definition from YAML

        Returns:
            Dictionary with file upload action
        """
        return {
            "action": "upload_file",
            "field_name": field_name,
            "file_data": file_data,
            "file_name": file_name,
            "content_type": content_type,
            "xpath": field_def.get("xpath"),
        }

    def get_platform_fields(self, platform: str) -> List[str]:
        """Get list of field names for a platform.

        Args:
            platform: Platform name (linkedin, indeed, glassdoor)

        Returns:
            List of field names available for the platform
        """
        platform_templates = self.templates.get(platform, {})
        return list(platform_templates.keys())

    def get_field_definition(
        self, platform: str, field_name: str
    ) -> Optional[Dict[str, str]]:
        """Get field definition from loaded templates.

        Args:
            platform: Platform name (linkedin, indeed, glassdoor)
            field_name: Name of the field to look up

        Returns:
            Field definition if found, None otherwise
        """
        platform_templates = self.templates.get(platform, {})
        return platform_templates.get(field_name)

    def get_mapped_answers(self, platform: str, field_name: str) -> List[str]:
        """Get mapped answer options for a field.

        Args:
            platform: Platform name (linkedin, indeed, glassdoor)
            field_name: Name of the field to look up

        Returns:
            List of mapped answers if available, empty list otherwise
        """
        platform_templates = self.templates.get(platform, {})
        field_def = platform_templates.get(field_name)

        if field_def:
            return field_def.get("answers", [])

        return []

    def is_ai_fallback_enabled(self, platform: str, field_name: str) -> bool:
        """Check if AI fallback is enabled for a field.

        Args:
            platform: Platform name
            field_name: Name of the field

        Returns:
            True if AI fallback enabled, False otherwise
        """
        platform_templates = self.templates.get(platform, {})
        field_def = platform_templates.get(field_name)

        if field_def:
            return field_def.get("ai_fallback", False)

        return False

    def validate_form_structure(self, platform: str) -> Dict[str, bool]:
        """Validate form structure for a platform.

        Args:
            platform: Platform name (linkedin, indeed, glassdoor)

        Returns:
            Dictionary with validation results for each required field
        """
        platform_templates = self.templates.get(platform, {})
        validation_results = {}

        # Check for required fields
        required_fields = platform_templates.keys()

        for field_name in required_fields:
            field_def = platform_templates.get(field_name, {})
            field_type = field_def.get("type")
            has_answers = field_def.get("answers")
            has_ai_fallback = field_def.get("ai_fallback", False)

            is_valid = (
                field_def  # Field definition exists
                and field_type  # Has type defined
                and (has_answers or has_ai_fallback)  # Has answer source
            )

            validation_results[field_name] = {
                "is_valid": is_valid,
                "has_mapped_answers": bool(has_answers),
                "has_ai_fallback": bool(has_ai_fallback),
                "field_type": field_type,
            }

        return validation_results

    async def get_field_completion_status(
        self,
        platform: str,
        filled_fields: Dict[str, str],
    ) -> Dict[str, Dict[str, str]]:
        """Get completion status for all fields in a form.

        Args:
            platform: Platform name
            filled_fields: Dictionary of filled field names to values

        Returns:
            Dictionary with completion status for each field
            Format: {field_name: {is_complete: bool, is_valid: bool}}
        """
        platform_templates = self.templates.get(platform, {})
        completion_status = {}

        for field_name, field_def in platform_templates.items():
            # Check if field is filled
            is_filled = (
                field_name in filled_fields and filled_fields[field_name] is not None
            )

            # Check if value is valid (non-empty string, not just whitespace)
            is_valid = True
            if is_filled:
                value = filled_fields[field_name]
                if isinstance(value, str):
                    is_valid = bool(value.strip())
                else:
                    is_valid = True

            completion_status[field_name] = {
                "is_complete": is_filled,
                "is_valid": is_valid,
                "field_type": field_def.get("type"),
            }

        return completion_status

    async def generate_form_preview(
        self,
        platform: str,
        user_preferences: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Generate a preview of form with auto-filled values.

        Args:
            platform: Platform name
            user_preferences: Optional user-provided values

        Returns:
            Dictionary with field names and auto-filled values
        """
        platform_templates = self.templates.get(platform, {})
        preview = {}

        for field_name, field_def in platform_templates.items():
            # Get auto-filled value (from YAML default or AI generation)
            if user_preferences and field_name in user_preferences:
                value = user_preferences[field_name]
            else:
                # Use mapped answers or AI fallback
                mapped_answers = field_def.get("answers", [])
                ai_fallback = field_def.get("ai_fallback", False)

                if mapped_answers:
                    # Use first non-empty mapped answer
                    value = next((a for a in mapped_answers if a and a.strip()), None)
                elif ai_fallback:
                    # Placeholder for AI preview (would need to call AI service)
                    value = "[AI Generated - Would require AI service call]"
                else:
                    # Use default value
                    value = field_def.get("default_value", "")

            if value:
                preview[field_name] = value

        return preview

    def reload_templates(self) -> None:
        """Reload form templates from YAML file.

        Useful for development or when YAML configuration changes.
        """
        self.templates = self._load_form_templates()
        self.logger.info("Form templates reloaded")
