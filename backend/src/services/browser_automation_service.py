"""Browser automation service for automated job applications using Playwright."""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from src.utils.logger import get_logger


@dataclass
class BrowserConfig:
    """Configuration for browser automation."""

    headless: bool = True
    user_data_dir: Optional[str] = None
    viewport_width: int = 1920
    viewport_height: int = 1080
    locale: str = "en-US"
    timezone_id: str = "America/New_York"
    disable_extensions: bool = True
    disable_gpu: bool = True


@dataclass
class FormField:
    """Detected form field information."""

    name: str
    type: str
    selector: str
    label: Optional[str] = None
    required: bool = False
    autocomplete: Optional[str] = None


class BrowserManager:
    """Manages Playwright browser instance with anti-detection measures."""

    def __init__(self, config: Optional[BrowserConfig] = None):
        """Initialize browser manager."""
        self.logger = get_logger(__name__)
        self.config = config or BrowserConfig()
        self.browser = None
        self.context = None
        self.page = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize browser with anti-detection measures."""
        try:
            from playwright.async_api import async_playwright

            self.logger.info("Initializing browser with anti-detection measures...")

            playwright = await async_playwright().start()

            # Launch browser with stealth settings
            self.browser = await playwright.chromium.launch(
                headless=self.config.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                    "--window-size=1920,1080",
                    "--start-maximized",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
            )

            # Create context with realistic browser properties
            self.context = await self.browser.new_context(
                viewport={
                    "width": self.config.viewport_width,
                    "height": self.config.viewport_height,
                },
                locale=self.config.locale,
                timezone_id=self.config.timezone_id,
                java_script_enabled=True,
                cookies=[],  # Start with clean cookies
                ignore_https_errors=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                device_scale_factor=1.0,
                has_touch=False,
                is_mobile=False,
            )

            # Add anti-detection script
            self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                window.chrome = {
                    runtime: {},
                    app: { isInstalled: true },
                    loadTimes: function() { return {}; },
                    csi: function() { return {}; },
                };
            """)

            self.page = await self.context.new_page()

            # Set default timeout
            self.page.set_default_timeout(30000)
            self.page.set_default_navigation_timeout(60000)

            self._initialized = True
            self.logger.info("Browser initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}", exc_info=True)
            return False

    async def navigate_to(self, url: str, wait_until: str = "networkidle") -> bool:
        """Navigate to a URL with human-like behavior."""
        try:
            self.logger.info(f"Navigating to: {url}")

            # Add random delay before navigation
            await self._human_delay(500, 1500)

            # Navigate with realistic timing
            await self.page.goto(url, wait_until=wait_until, timeout=60000)

            # Random scroll to simulate human behavior
            await self._human_scroll()

            return True

        except Exception as e:
            self.logger.error(f"Navigation failed: {e}", exc_info=True)
            return False

    async def find_form_fields(self) -> List[FormField]:
        """Detect and extract form fields from current page."""
        try:
            fields = []

            # Find all input fields
            input_selectors = [
                "input:not([type='hidden']):not([type='submit'])",
                "textarea",
                "select",
            ]

            for selector in input_selectors:
                elements = await self.page.query_selector_all(selector)

                for element in elements:
                    field = await self._analyze_field(element, selector)
                    if field:
                        fields.append(field)

            self.logger.info(f"Found {len(fields)} form fields")
            return fields

        except Exception as e:
            self.logger.error(f"Failed to find form fields: {e}", exc_info=True)
            return []

    async def fill_form_field(self, selector: str, value: str) -> bool:
        """Fill a form field with human-like behavior."""
        try:
            # Clear existing value
            await self.page.click(selector)
            await self.page.keyboard.press("Control+a")
            await self.page.keyboard.press("Backspace")

            # Type with random delays
            await self.page.type(selector, value, delay=50)

            return True

        except Exception as e:
            self.logger.error(f"Failed to fill form field: {e}", exc_info=True)
            return False

    async def upload_file(self, selector: str, file_path: str) -> bool:
        """Upload a file to file input."""
        try:
            file_input = await self.page.query_selector(selector)
            if file_input:
                await file_input.set_input_files(file_path)
                self.logger.info(f"Uploaded file: {file_path}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Failed to upload file: {e}", exc_info=True)
            return False

    async def click_element(self, selector: str) -> bool:
        """Click an element with human-like behavior."""
        try:
            # Add random delay before clicking
            await self._human_delay(200, 500)

            # Scroll element into view
            await self.page.evaluate(
                f"""
                (selector) => {{
                    const el = document.querySelector(selector);
                    if (el) {{
                        el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}
                }}
            """,
                selector,
            )

            await self._human_delay(100, 300)

            # Click
            await self.page.click(selector, force=True)

            return True

        except Exception as e:
            self.logger.error(f"Failed to click element: {e}", exc_info=True)
            return False

    async def wait_for_element(self, selector: str, timeout: int = 30000) -> bool:
        """Wait for an element to appear."""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            self.logger.error(f"Element not found: {selector}")
            return False

    async def take_screenshot(self, path: str) -> bool:
        """Take a screenshot of current page."""
        try:
            await self.page.screenshot(path=path, full_page=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return False

    async def get_page_content(self) -> str:
        """Get current page HTML content."""
        try:
            return await self.page.content()
        except Exception as e:
            self.logger.error(f"Failed to get page content: {e}")
            return ""

    async def close(self) -> None:
        """Close browser and cleanup resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()

            self._initialized = False
            self.logger.info("Browser closed successfully")

        except Exception as e:
            self.logger.error(f"Error closing browser: {e}", exc_info=True)

    async def _human_delay(self, min_ms: int = 100, max_ms: int = 500) -> None:
        """Add random delay to simulate human behavior."""
        import random

        delay = random.uniform(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)

    async def _human_scroll(self) -> None:
        """Perform random scroll to simulate human reading behavior."""
        import random

        for _ in range(random.randint(1, 3)):
            scroll_amount = random.randint(200, 500)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await self._human_delay(300, 800)

    async def _analyze_field(self, element, base_selector: str) -> Optional[FormField]:
        """Analyze a form field to extract its properties."""
        try:
            field_info = await element.evaluate("""(el) => {{
                return {{
                    name: el.name || el.id || '',
                    type: el.type || 'text',
                    selector: get_selector(el),
                    label: get_label(el),
                    required: el.required,
                    autocomplete: el.autocomplete || null
                }};
                
                function get_selector(el) {{
                    if (el.id) return '#' + el.id;
                    if (el.name) return `[name="${el.name}"]`;
                    return el.tagName.toLowerCase() + ':nth-of-type(1)';
                }}
                
                function get_label(el) {{
                    const label = el.closest('label');
                    if (label) return label.textContent.trim();
                    const label_for = document.querySelector(`[for="${el.id}"]`);
                    if (label_for) return label_for.textContent.trim();
                    return null;
                }}
            }}""")

            return FormField(
                name=field_info["name"],
                type=field_info["type"],
                selector=field_info["selector"],
                label=field_info["label"],
                required=field_info["required"],
                autocomplete=field_info["autocomplete"],
            )

        except Exception:
            return None


class FormFieldDetector:
    """AI-powered form field detection and mapping."""

    def __init__(self):
        """Initialize form field detector."""
        self.logger = get_logger(__name__)

        # Field name mappings for different platforms
        self.field_mappings = {
            "full_name": [
                "fullname",
                "full_name",
                "name",
                "candidate_name",
                "applicant_name",
                "your_name",
            ],
            "first_name": ["firstname", "first_name", "fname", "given_name"],
            "last_name": ["lastname", "last_name", "lname", "surname", "family_name"],
            "email": ["email", "email_address", "emailaddress", "your_email"],
            "phone": [
                "phone",
                "phone_number",
                "telephone",
                "mobile",
                "cell",
                "phone_number",
            ],
            "address": ["address", "street", "location", "home_address"],
            "city": ["city", "town", " municipality"],
            "state": ["state", "province", "region"],
            "zip_code": ["zip", "zip_code", "postal", "postal_code", "postcode"],
            "country": ["country", "nation"],
            "resume": [
                "resume",
                "cv",
                "curriculum_vitae",
                "upload_resume",
                "attach_resume",
                "file_upload",
            ],
            "cover_letter": ["cover_letter", "coverletter", "cover", "letter"],
            "linkedin": ["linkedin", "linkedin_url", "linkedin_profile"],
            "portfolio": ["portfolio", "website", "personal_site", "github"],
            "experience": ["years_experience", "experience_years", "total_experience"],
            "education": ["education", "degree", "school", "university"],
        }

    async def detect_and_map(
        self, fields: List[FormField], resume_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Detect form fields and map them to resume data.

        Args:
            fields: List of detected form fields
            resume_data: User's resume/profile data

        Returns:
            Dictionary mapping field selectors to values
        """
        field_mapping = {}

        for field in fields:
            # Find matching resume data
            value = self._find_matching_value(field, resume_data)
            if value is not None:
                field_mapping[field.selector] = value

        self.logger.info(f"Mapped {len(field_mapping)} fields to resume data")
        return field_mapping

    def _find_matching_value(
        self, field: FormField, resume_data: Dict[str, Any]
    ) -> Optional[str]:
        """Find matching value from resume data for a form field."""
        field_name_lower = field.name.lower()

        # Check against field mappings
        for mapping_key, aliases in self.field_mappings.items():
            if field_name_lower in aliases:
                # Get value from resume data
                return resume_data.get(mapping_key) or resume_data.get(field.name)

        # Direct field name match
        if field_name_lower in resume_data:
            return resume_data[field_name_lower]

        # Check for partial matches
        for key, value in resume_data.items():
            if field_name_lower in key.lower() or key.lower() in field_name_lower:
                return value

        return None


class BrowserAutomationService:
    """Main service for automated job applications using browser automation."""

    def __init__(self):
        """Initialize browser automation service."""
        self.logger = get_logger(__name__)
        self.browser_manager = BrowserManager()
        self.field_detector = FormFieldDetector()
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the browser automation service."""
        try:
            success = await self.browser_manager.initialize()
            self._initialized = success
            return success
        except Exception as e:
            self.logger.error(
                f"Failed to initialize browser automation: {e}", exc_info=True
            )
            return False

    async def close(self) -> None:
        """Close the browser automation service."""
        await self.browser_manager.close()
        self._initialized = False

    async def apply_to_job(
        self,
        job_url: str,
        resume_path: str,
        cover_letter_path: str,
        profile_data: Dict[str, Any],
        platform: str = "generic",
    ) -> Dict[str, Any]:
        """
        Apply to a job using browser automation.

        Args:
            job_url: URL of the job application page
            resume_path: Path to resume file
            cover_letter_path: Path to cover letter file
            profile_data: User's profile data
            platform: Job platform (linkedin, indeed, glassdoor, etc.)

        Returns:
            Application result with status and details
        """
        try:
            self.logger.info(f"Starting automated application to: {job_url}")

            if not self._initialized:
                await self.initialize()

            # Navigate to job page
            success = await self.browser_manager.navigate_to(job_url)
            if not success:
                return {"success": False, "error": "Failed to navigate to job page"}

            # Detect and fill form fields
            form_fields = await self.browser_manager.find_form_fields()
            field_mapping = await self.field_detector.detect_and_map(
                form_fields, profile_data
            )

            # Fill all mapped fields
            for selector, value in field_mapping.items():
                await self.browser_manager.fill_form_field(selector, str(value))

            # Upload resume if field found
            resume_field = self._find_field_by_name(
                form_fields, ["resume", "cv", "file_upload"]
            )
            if resume_field:
                await self.browser_manager.upload_file(
                    resume_field.selector, resume_path
                )

            # Upload cover letter if field found
            cover_letter_field = self._find_field_by_name(
                form_fields, ["cover_letter", "cover", "letter"]
            )
            if cover_letter_field:
                await self.browser_manager.upload_file(
                    cover_letter_field.selector, cover_letter_path
                )

            # Find and click submit button
            submit_button = await self._find_submit_button()
            if submit_button:
                await self.browser_manager.click_element(submit_button)
                await asyncio.sleep(2000)  # Wait for submission

            # Take screenshot for verification
            screenshot_path = f"/tmp/application_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.browser_manager.take_screenshot(screenshot_path)

            return {
                "success": True,
                "platform": platform,
                "url": job_url,
                "screenshot": screenshot_path,
                "fields_filled": len(field_mapping),
                "resume_uploaded": bool(resume_field),
                "cover_letter_uploaded": bool(cover_letter_field),
            }

        except Exception as e:
            self.logger.error(f"Automated application failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _find_field_by_name(
        self, fields: List[FormField], names: List[str]
    ) -> Optional[FormField]:
        """Find a form field by name from list of possible names."""
        for field in fields:
            if field.name.lower() in names:
                return field
        return None

    async def _find_submit_button(self) -> Optional[str]:
        """Find submit button selector."""
        button_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            ".submit-button",
            "#submit",
            "[type='submit']",
            ".apply-button",
            "#apply",
            "button:has-text('Submit')",
            "button:has-text('Apply')",
            "button:has-text('Send')",
        ]

        for selector in button_selectors:
            try:
                element = await self.browser_manager.page.query_selector(selector)
                if element:
                    return selector
            except:
                continue

        return None

    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        return {
            "status": "healthy" if self._initialized else "unhealthy",
            "initialized": self._initialized,
            "browser_available": self.browser_manager.browser is not None,
        }
