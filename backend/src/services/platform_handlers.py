"""Platform-specific job application handlers for different job portals."""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from abc import ABC, abstractmethod

from src.utils.logger import get_logger
from src.services.browser_automation_service import BrowserManager, FormFieldDetector


class BasePlatformHandler(ABC):
    """Base class for platform-specific job application handlers."""

    def __init__(
        self, browser_manager: BrowserManager, field_detector: FormFieldDetector
    ):
        """Initialize platform handler."""
        self.browser = browser_manager
        self.field_detector = field_detector
        self.logger = get_logger(__name__)

    @abstractmethod
    async def handle_application(
        self,
        job_url: str,
        resume_path: str,
        cover_letter_path: str,
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle job application for this platform."""
        pass

    @abstractmethod
    async def login(self, credentials: Dict[str, str]) -> bool:
        """Login to the platform if required."""
        pass

    @abstractmethod
    async def is_logged_in(self) -> bool:
        """Check if currently logged in."""
        pass

    async def _human_delay(self, min_ms: int = 100, max_ms: int = 500) -> None:
        """Add random delay to simulate human behavior."""
        import random

        delay = random.uniform(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)


class LinkedInHandler(BasePlatformHandler):
    """Handler for LinkedIn job applications."""

    PLATFORM_NAME = "linkedin"
    LOGIN_URL = "https://www.linkedin.com/login"

    async def handle_application(
        self,
        job_url: str,
        resume_path: str,
        cover_letter_path: str,
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle LinkedIn job application."""
        try:
            self.logger.info(f"Processing LinkedIn application: {job_url}")

            # Navigate to job page
            await self.browser.navigate_to(job_url)

            # Wait for page to load
            await asyncio.sleep(2000)

            # Try to find and click "Easy Apply" button
            easy_apply_selector = await self._find_easy_apply_button()
            if easy_apply_selector:
                return await self._handle_easy_apply(
                    easy_apply_selector, resume_path, cover_letter_path, profile_data
                )

            # If no easy apply, try regular apply
            apply_selector = await self._find_apply_button()
            if apply_selector:
                return await self._handle_regular_apply(
                    apply_selector, resume_path, cover_letter_path, profile_data
                )

            # If redirected to external site
            external_url = await self._check_external_redirect()
            if external_url:
                return {
                    "success": True,
                    "method": "external_redirect",
                    "redirect_url": external_url,
                    "message": "Application redirects to company website",
                }

            return {"success": False, "error": "No application method found"}

        except Exception as e:
            self.logger.error(f"LinkedIn application failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def login(self, credentials: Dict[str, str]) -> bool:
        """Login to LinkedIn."""
        try:
            username = credentials.get("username")
            password = credentials.get("password")

            if not username or not password:
                self.logger.error("Missing username or password")
                return False

            await self.browser.navigate_to(self.LOGIN_URL)

            # Wait for login page to load
            await self.browser.wait_for_element("#username")

            # Enter credentials with human-like delays
            await self.browser.fill_form_field("#username", username)
            await self._human_delay(200, 500)
            await self.browser.fill_form_field("#password", password)

            # Click login button
            await self.browser.click_element("button[type='submit']")

            # Wait for navigation
            await asyncio.sleep(3000)

            # Check if login successful
            return await self.is_logged_in()

        except Exception as e:
            self.logger.error(f"LinkedIn login failed: {e}", exc_info=True)
            return False

    async def is_logged_in(self) -> bool:
        """Check if logged into LinkedIn."""
        try:
            # Check for feed or profile icon
            feed_element = await self.browser.page.query_selector(
                ".feed-identity-module"
            )
            profile_element = await self.browser.page.query_selector(
                "#profile-nav-item"
            )
            return feed_element is not None or profile_element is not None
        except:
            return False

    async def _find_easy_apply_button(self) -> Optional[str]:
        """Find Easy Apply button on job page."""
        selectors = [
            "button.jobs-apply-button",
            "button[data-test='apply-button']",
            ".jobs-apply-button",
            "button:has-text('Easy Apply')",
            "button:has-text('Apply')",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        return selector
            except:
                continue

        return None

    async def _find_apply_button(self) -> Optional[str]:
        """Find regular Apply button on job page."""
        selectors = [
            "button[data-test='apply-now-button']",
            ".apply-button",
            "a:has-text('Apply')",
            "button:has-text('Apply now')",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        return selector
            except:
                continue

        return None

    async def _handle_easy_apply(
        self,
        button_selector: str,
        resume_path: str,
        cover_letter_path: str,
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle Easy Apply process."""
        # Click the Easy Apply button
        await self.browser.click_element(button_selector)
        await asyncio.sleep(1500)

        # Process multi-step form
        step = 0
        max_steps = 5

        while step < max_steps:
            # Fill current step
            await self._fill_current_step(profile_data, resume_path, cover_letter_path)

            # Find and click next button
            next_button = await self._find_next_button()
            if not next_button:
                break

            await self.browser.click_element(next_button)
            await asyncio.sleep(1500)
            step += 1

        # Find and click submit button
        submit_button = await self._find_submit_button()
        if submit_button:
            await self.browser.click_element(submit_button)
            await asyncio.sleep(2000)

        return {
            "success": True,
            "method": "easy_apply",
            "steps_completed": step,
            "resume_uploaded": bool(resume_path),
        }

    async def _handle_regular_apply(
        self,
        button_selector: str,
        resume_path: str,
        cover_letter_path: str,
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle regular Apply process."""
        # Click the Apply button
        await self.browser.click_element(button_selector)
        await asyncio.sleep(2000)

        # Wait for modal or new page
        await self.browser.wait_for_element("body")

        # Detect form fields and fill
        form_fields = await self.browser.find_form_fields()
        field_mapping = await self.field_detector.detect_and_map(
            form_fields, profile_data
        )

        for selector, value in field_mapping.items():
            await self.browser.fill_form_field(selector, str(value))

        # Upload resume if required
        resume_field = await self._find_resume_upload_field()
        if resume_field and resume_path:
            await self.browser.upload_file(resume_field, resume_path)

        # Submit application
        submit_button = await self._find_submit_button()
        if submit_button:
            await self.browser.click_element(submit_button)
            await asyncio.sleep(2000)

        return {
            "success": True,
            "method": "regular_apply",
            "fields_filled": len(field_mapping),
        }

    async def _fill_current_step(
        self, profile_data: Dict[str, Any], resume_path: str, cover_letter_path: str
    ) -> None:
        """Fill current form step."""
        # Detect form fields
        form_fields = await self.browser.find_form_fields()
        field_mapping = await self.field_detector.detect_and_map(
            form_fields, profile_data
        )

        # Fill all mapped fields
        for selector, value in field_mapping.items():
            await self.browser.fill_form_field(selector, str(value))

        # Upload resume if needed
        if resume_path:
            resume_field = await self._find_resume_upload_field()
            if resume_field:
                await self.browser.upload_file(resume_field, resume_path)

    async def _find_next_button(self) -> Optional[str]:
        """Find Next button in multi-step form."""
        selectors = [
            "button[data-test='continue-button']",
            "button:has-text('Next')",
            "button:has-text('Continue')",
            ".continue-btn",
            "button[type='button']:has-text('Next')",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element and await element.is_visible():
                    return selector
            except:
                continue

        return None

    async def _find_submit_button(self) -> Optional[str]:
        """Find Submit button."""
        selectors = [
            "button[data-test='submit-application-button']",
            "button:has-text('Submit')",
            "button:has-text('Submit application')",
            ".submit-button",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element and await element.is_visible():
                    return selector
            except:
                continue

        return None

    async def _find_resume_upload_field(self) -> Optional[str]:
        """Find resume upload field."""
        selectors = [
            "input[type='file'][accept*='pdf']",
            "input[name='resume']",
            "input[name='cv']",
            "input[type='file']",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element:
                    return selector
            except:
                continue

        return None

    async def _check_external_redirect(self) -> Optional[str]:
        """Check if redirected to external application site."""
        try:
            # Check current URL
            current_url = self.browser.page.url

            if "linkedin.com" not in current_url:
                return current_url

            # Check for redirect message
            redirect_element = await self.browser.page.query_selector(
                ".jobs-external-application-warning"
            )
            if redirect_element:
                return current_url

            return None

        except:
            return None


class IndeedHandler(BasePlatformHandler):
    """Handler for Indeed job applications."""

    PLATFORM_NAME = "indeed"
    LOGIN_URL = "https://secure.indeed.com/auth"

    async def handle_application(
        self,
        job_url: str,
        resume_path: str,
        cover_letter_path: str,
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle Indeed job application."""
        try:
            self.logger.info(f"Processing Indeed application: {job_url}")

            await self.browser.navigate_to(job_url)
            await asyncio.sleep(2000)

            # Find and click Apply button
            apply_button = await self._find_apply_button()
            if not apply_button:
                return {"success": False, "error": "Apply button not found"}

            await self.browser.click_element(apply_button)
            await asyncio.sleep(2000)

            # Check if external application
            if await self._is_external_application():
                external_url = await self._get_external_url()
                if external_url:
                    return {
                        "success": True,
                        "method": "external_redirect",
                        "redirect_url": external_url,
                        "message": "Application redirects to company website",
                    }

            # Fill application form
            return await self._fill_application_form(
                resume_path, cover_letter_path, profile_data
            )

        except Exception as e:
            self.logger.error(f"Indeed application failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def login(self, credentials: Dict[str, str]) -> bool:
        """Login to Indeed."""
        try:
            username = credentials.get("username")
            password = credentials.get("password")

            if not username or not password:
                return False

            await self.browser.navigate_to(self.LOGIN_URL)
            await self.browser.wait_for_element("#email")

            await self.browser.fill_form_field("#email", username)
            await self._human_delay(200, 500)
            await self.browser.fill_form_field("#password", password)

            await self.browser.click_element("button[type='submit']")
            await asyncio.sleep(3000)

            return await self.is_logged_in()

        except Exception as e:
            self.logger.error(f"Indeed login failed: {e}", exc_info=True)
            return False

    async def is_logged_in(self) -> bool:
        """Check if logged into Indeed."""
        try:
            # Check for user menu or profile element
            user_menu = await self.browser.page.query_selector(".user-nav-item")
            return user_menu is not None
        except:
            return False

    async def _find_apply_button(self) -> Optional[str]:
        """Find Apply button on Indeed job page."""
        selectors = [
            ".indeed-apply-button",
            "button:has-text('Apply')",
            "a:has-text('Apply')",
            "[data-testid='apply-button']",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element and await element.is_visible():
                    return selector
            except:
                continue

        return None

    async def _is_external_application(self) -> bool:
        """Check if application redirects externally."""
        try:
            external_element = await self.browser.page.query_selector(
                ".indeed-apply-notice-external"
            )
            return external_element is not None
        except:
            return False

    async def _get_external_url(self) -> Optional[str]:
        """Get external application URL."""
        try:
            apply_link = await self.browser.page.query_selector(
                ".indeed-apply-notice-external a"
            )
            if apply_link:
                return await apply_link.get_attribute("href")
            return None
        except:
            return None

    async def _fill_application_form(
        self, resume_path: str, cover_letter_path: str, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fill Indeed application form."""
        # Detect form fields
        form_fields = await self.browser.find_form_fields()
        field_mapping = await self.field_detector.detect_and_map(
            form_fields, profile_data
        )

        # Fill all mapped fields
        for selector, value in field_mapping.items():
            await self.browser.fill_form_field(selector, str(value))

        # Upload resume if needed
        if resume_path:
            resume_field = await self._find_resume_upload_field()
            if resume_field:
                await self.browser.upload_file(resume_field, resume_path)

        # Submit application
        submit_button = await self._find_submit_button()
        if submit_button:
            await self.browser.click_element(submit_button)
            await asyncio.sleep(2000)

        return {
            "success": True,
            "method": "indeed_form",
            "fields_filled": len(field_mapping),
        }

    async def _find_submit_button(self) -> Optional[str]:
        """Find Submit button."""
        selectors = [
            "button[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Send Application')",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element and await element.is_visible():
                    return selector
            except:
                continue

        return None

    async def _find_resume_upload_field(self) -> Optional[str]:
        """Find resume upload field."""
        selectors = [
            "input[type='file']",
            "input[name='resume']",
            "input[accept*='pdf']",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element:
                    return selector
            except:
                continue

        return None


class GlassdoorHandler(BasePlatformHandler):
    """Handler for Glassdoor job applications."""

    PLATFORM_NAME = "glassdoor"
    LOGIN_URL = "https://www.glassdoor.com/profile/login"

    async def handle_application(
        self,
        job_url: str,
        resume_path: str,
        cover_letter_path: str,
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle Glassdoor job application."""
        try:
            self.logger.info(f"Processing Glassdoor application: {job_url}")

            await self.browser.navigate_to(job_url)
            await asyncio.sleep(2000)

            # Check for external application
            if await self._is_external_application():
                external_url = await self._get_external_url()
                if external_url:
                    return {
                        "success": True,
                        "method": "external_redirect",
                        "redirect_url": external_url,
                        "message": "Application redirects to company website",
                    }

            # Find and click Apply button
            apply_button = await self._find_apply_button()
            if not apply_button:
                return {"success": False, "error": "Apply button not found"}

            await self.browser.click_element(apply_button)
            await asyncio.sleep(2000)

            # Fill application form
            return await self._fill_application_form(
                resume_path, cover_letter_path, profile_data
            )

        except Exception as e:
            self.logger.error(f"Glassdoor application failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def login(self, credentials: Dict[str, str]) -> bool:
        """Login to Glassdoor."""
        try:
            username = credentials.get("username")
            password = credentials.get("password")

            if not username or not password:
                return False

            await self.browser.navigate_to(self.LOGIN_URL)
            await self.browser.wait_for_element("#email")

            await self.browser.fill_form_field("#email", username)
            await self._human_delay(200, 500)
            await self.browser.fill_form_field("#password", password)

            await self.browser.click_element("button[type='submit']")
            await asyncio.sleep(3000)

            return await self.is_logged_in()

        except Exception as e:
            self.logger.error(f"Glassdoor login failed: {e}", exc_info=True)
            return False

    async def is_logged_in(self) -> bool:
        """Check if logged into Glassdoor."""
        try:
            # Check for user avatar or profile element
            profile_element = await self.browser.page.query_selector(
                "[data-test='user-nav-avatar']"
            )
            return profile_element is not None
        except:
            return False

    async def _find_apply_button(self) -> Optional[str]:
        """Find Apply button on Glassdoor job page."""
        selectors = [
            "button:has-text('Apply')",
            "a:has-text('Apply')",
            "[data-test='apply-button']",
            ".applyButton",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element and await element.is_visible():
                    return selector
            except:
                continue

        return None

    async def _is_external_application(self) -> bool:
        """Check if application redirects externally."""
        try:
            # Check for "Apply on company site" message
            external_element = await self.browser.page.query_selector(".externalApply")
            return external_element is not None
        except:
            return False

    async def _get_external_url(self) -> Optional[str]:
        """Get external application URL."""
        try:
            apply_link = await self.browser.page.query_selector(".externalApply a")
            if apply_link:
                return await apply_link.get_attribute("href")
            return None
        except:
            return None

    async def _fill_application_form(
        self, resume_path: str, cover_letter_path: str, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fill Glassdoor application form."""
        # Detect form fields
        form_fields = await self.browser.find_form_fields()
        field_mapping = await self.field_detector.detect_and_map(
            form_fields, profile_data
        )

        # Fill all mapped fields
        for selector, value in field_mapping.items():
            await self.browser.fill_form_field(selector, str(value))

        # Upload resume if needed
        if resume_path:
            resume_field = await self._find_resume_upload_field()
            if resume_field:
                await self.browser.upload_file(resume_field, resume_path)

        # Submit application
        submit_button = await self._find_submit_button()
        if submit_button:
            await self.browser.click_element(submit_button)
            await asyncio.sleep(2000)

        return {
            "success": True,
            "method": "glassdoor_form",
            "fields_filled": len(field_mapping),
        }

    async def _find_submit_button(self) -> Optional[str]:
        """Find Submit button."""
        selectors = [
            "button[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Send Application')",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element and await element.is_visible():
                    return selector
            except:
                continue

        return None

    async def _find_resume_upload_field(self) -> Optional[str]:
        """Find resume upload field."""
        selectors = [
            "input[type='file']",
            "input[name='resume']",
            "input[accept*='pdf']",
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element:
                    return selector
            except:
                continue

        return None


def create_platform_handler(
    platform: str, browser_manager: BrowserManager, field_detector: FormFieldDetector
) -> BasePlatformHandler:
    """
    Factory function to create platform-specific handler.

    Args:
        platform: Platform name (linkedin, indeed, glassdoor)
        browser_manager: Browser manager instance
        field_detector: Form field detector instance

    Returns:
        Platform handler instance
    """
    handlers = {
        "linkedin": LinkedInHandler,
        "indeed": IndeedHandler,
        "glassdoor": GlassdoorHandler,
    }

    handler_class = handlers.get(platform.lower())
    if handler_class:
        return handler_class(browser_manager, field_detector)

    raise ValueError(f"Unknown platform: {platform}")
