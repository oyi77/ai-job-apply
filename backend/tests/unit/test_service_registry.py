"""Unit tests for the ServiceRegistry following TDD principles.

Tests cover:
- Service registry initialization
- Service registration and retrieval
- Health checks
- Graceful shutdown
- Dependency injection
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

# Import the modules to test
from src.services.service_registry import (
    ServiceRegistry,
    ServiceProvider,
    LocalFileServiceProvider,
    GeminiAIProvider,
    ResumeServiceProvider,
    ApplicationServiceProvider,
    CoverLetterServiceProvider,
    JobSearchServiceProvider,
    JobApplicationServiceProvider,
)


class MockServiceProvider(ServiceProvider):
    """Mock service provider for testing."""
    
    def __init__(self, service_name: str = "mock_service"):
        self.service_name = service_name
        self._service = MagicMock()
        self._service.name = service_name
        self.initialized = False
        self.cleaned_up = False
    
    def get_service(self) -> Any:
        return self._service
    
    async def initialize(self) -> None:
        self.initialized = True
    
    async def cleanup(self) -> None:
        self.cleaned_up = True


class TestServiceRegistry:
    """Test suite for ServiceRegistry class."""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh ServiceRegistry instance."""
        return ServiceRegistry()
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock service provider."""
        return MockServiceProvider()
    
    # =========================================================================
    # Test: Service Registry Initialization
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_registry_starts_uninitialized(self, registry):
        """Registry should start in uninitialized state."""
        assert registry._initialized is False
        assert len(registry._services) == 0
        assert len(registry._instances) == 0
    
    @pytest.mark.asyncio
    async def test_register_service(self, registry, mock_provider):
        """Service can be registered with the registry."""
        registry.register_service("test_service", mock_provider)
        
        assert "test_service" in registry._services
        assert registry._services["test_service"] == mock_provider
    
    @pytest.mark.asyncio
    async def test_register_multiple_services(self, registry):
        """Multiple services can be registered."""
        provider1 = MockServiceProvider("service1")
        provider2 = MockServiceProvider("service2")
        
        registry.register_service("service1", provider1)
        registry.register_service("service2", provider2)
        
        assert len(registry._services) == 2
        assert "service1" in registry._services
        assert "service2" in registry._services
    
    @pytest.mark.asyncio
    @patch('src.services.service_registry.LocalFileServiceProvider')
    @patch('src.services.service_registry.GeminiAIProvider')
    async def test_initialize_sets_initialized_flag(self, mock_ai, mock_file, registry):
        """Initialize should set the initialized flag to True."""
        # Setup mocks
        mock_file_instance = AsyncMock()
        mock_file_instance.get_service.return_value = MagicMock()
        mock_file.return_value = mock_file_instance
        
        mock_ai_instance = AsyncMock()
        mock_ai_instance.get_service.return_value = MagicMock()
        mock_ai.return_value = mock_ai_instance
        
        # Patch the internal methods to avoid actual initialization
        with patch.object(registry, '_initialize_core_services', new_callable=AsyncMock):
            with patch.object(registry, '_initialize_business_services', new_callable=AsyncMock):
                await registry.initialize()
        
        assert registry._initialized is True
    
    @pytest.mark.asyncio
    async def test_initialize_only_runs_once(self, registry):
        """Initialize should only run once even if called multiple times."""
        with patch.object(registry, '_initialize_core_services', new_callable=AsyncMock) as mock_core:
            with patch.object(registry, '_initialize_business_services', new_callable=AsyncMock) as mock_business:
                await registry.initialize()
                await registry.initialize()  # Second call should not re-initialize
        
        # Should only be called once
        mock_core.assert_called_once()
        mock_business.assert_called_once()
    
    # =========================================================================
    # Test: Service Retrieval (Dependency Injection)
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_get_service_by_name(self, registry, mock_provider):
        """Services can be retrieved by name after initialization."""
        registry._initialized = True
        registry._instances["test_service"] = mock_provider.get_service()
        
        service = await registry.get_service("test_service")
        
        assert service is not None
        assert service.name == "mock_service"
    
    @pytest.mark.asyncio
    async def test_get_service_auto_initializes(self, registry):
        """Getting a service should auto-initialize if not already done."""
        with patch.object(registry, 'initialize', new_callable=AsyncMock) as mock_init:
            with pytest.raises(KeyError):
                await registry.get_service("nonexistent")
        
        mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_service_raises_for_unknown_service(self, registry):
        """KeyError should be raised for unknown service names."""
        registry._initialized = True
        
        with pytest.raises(KeyError, match="Service 'unknown' not found"):
            await registry.get_service("unknown")
    
    @pytest.mark.asyncio
    async def test_get_ai_service(self, registry):
        """get_ai_service convenience method works correctly."""
        mock_ai = MagicMock()
        registry._initialized = True
        registry._instances["ai_service"] = mock_ai
        
        service = await registry.get_ai_service()
        
        assert service == mock_ai
    
    @pytest.mark.asyncio
    async def test_get_file_service(self, registry):
        """get_file_service convenience method works correctly."""
        mock_file = MagicMock()
        registry._initialized = True
        registry._instances["file_service"] = mock_file
        
        service = await registry.get_file_service()
        
        assert service == mock_file
    
    @pytest.mark.asyncio
    async def test_get_resume_service(self, registry):
        """get_resume_service convenience method works correctly."""
        mock_resume = MagicMock()
        registry._initialized = True
        registry._instances["resume_service"] = mock_resume
        
        service = await registry.get_resume_service()
        
        assert service == mock_resume
    
    @pytest.mark.asyncio
    async def test_get_application_service(self, registry):
        """get_application_service convenience method works correctly."""
        mock_app = MagicMock()
        registry._initialized = True
        registry._instances["application_service"] = mock_app
        
        service = await registry.get_application_service()
        
        assert service == mock_app
    
    @pytest.mark.asyncio
    async def test_get_cover_letter_service(self, registry):
        """get_cover_letter_service convenience method works correctly."""
        mock_cover = MagicMock()
        registry._initialized = True
        registry._instances["cover_letter_service"] = mock_cover
        
        service = await registry.get_cover_letter_service()
        
        assert service == mock_cover
    
    @pytest.mark.asyncio
    async def test_get_job_search_service(self, registry):
        """get_job_search_service convenience method works correctly."""
        mock_job_search = MagicMock()
        registry._initialized = True
        registry._instances["job_search_service"] = mock_job_search
        
        service = await registry.get_job_search_service()
        
        assert service == mock_job_search
    
    @pytest.mark.asyncio
    async def test_get_job_application_service(self, registry):
        """get_job_application_service convenience method works correctly."""
        mock_job_app = MagicMock()
        registry._initialized = True
        registry._instances["job_application_service"] = mock_job_app
        
        service = await registry.get_job_application_service()
        
        assert service == mock_job_app
    
    # =========================================================================
    # Test: Health Checks
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_health_check_returns_healthy_status(self, registry):
        """Health check should return healthy status when services are OK."""
        # Create a mock with only is_available attribute (no health_check)
        mock_service = MagicMock(spec=['is_available'])
        mock_service.is_available = AsyncMock(return_value=True)
        
        registry._initialized = True
        registry._instances["test_service"] = mock_service
        
        health = await registry.health_check()
        
        assert health["service_registry"] == "healthy"
        assert "test_service" in health["services"]
        assert health["services"]["test_service"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_detects_degraded_service(self, registry):
        """Health check should detect degraded services."""
        # Create a mock with only is_available attribute (no health_check)
        mock_service = MagicMock(spec=['is_available'])
        mock_service.is_available = AsyncMock(return_value=False)
        
        registry._initialized = True
        registry._instances["failing_service"] = mock_service
        
        health = await registry.health_check()
        
        assert health["services"]["failing_service"]["status"] == "degraded"
        assert health["services"]["failing_service"]["available"] is False
    
    @pytest.mark.asyncio
    async def test_health_check_handles_service_with_health_check_method(self, registry):
        """Health check should use service's health_check method if available."""
        mock_service = MagicMock()
        mock_service.health_check = AsyncMock(return_value={"status": "healthy", "details": "ok"})
        
        registry._initialized = True
        registry._instances["detailed_service"] = mock_service
        
        health = await registry.health_check()
        
        assert health["services"]["detailed_service"]["status"] == "healthy"
        assert health["services"]["detailed_service"]["details"] == "ok"
    
    @pytest.mark.asyncio
    async def test_health_check_handles_service_exceptions(self, registry):
        """Health check should handle service exceptions gracefully."""
        mock_service = MagicMock()
        mock_service.is_available = AsyncMock(side_effect=Exception("Service error"))
        
        registry._initialized = True
        registry._instances["error_service"] = mock_service
        
        health = await registry.health_check()
        
        assert health["services"]["error_service"]["status"] == "unhealthy"
        assert "error" in health["services"]["error_service"]
    
    @pytest.mark.asyncio
    async def test_health_check_auto_initializes(self, registry):
        """Health check should auto-initialize if not already done."""
        with patch.object(registry, 'initialize', new_callable=AsyncMock) as mock_init:
            await registry.health_check()
        
        mock_init.assert_called_once()
    
    # =========================================================================
    # Test: Graceful Shutdown
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_shutdown_cleans_up_all_services(self, registry):
        """Shutdown should clean up all registered services."""
        provider1 = MockServiceProvider("service1")
        provider2 = MockServiceProvider("service2")
        
        registry._services = {"service1": provider1, "service2": provider2}
        registry._instances = {"service1": MagicMock(), "service2": MagicMock()}
        registry._initialized = True
        
        await registry.shutdown()
        
        assert provider1.cleaned_up is True
        assert provider2.cleaned_up is True
    
    @pytest.mark.asyncio
    async def test_shutdown_clears_instances(self, registry):
        """Shutdown should clear all service instances."""
        registry._services = {"test": MockServiceProvider()}
        registry._instances = {"test": MagicMock()}
        registry._initialized = True
        
        await registry.shutdown()
        
        assert len(registry._instances) == 0
        assert len(registry._services) == 0
        assert registry._initialized is False
    
    @pytest.mark.asyncio
    async def test_shutdown_handles_cleanup_errors(self, registry):
        """Shutdown should handle cleanup errors gracefully."""
        failing_provider = MockServiceProvider()
        failing_provider.cleanup = AsyncMock(side_effect=Exception("Cleanup failed"))
        
        registry._services = {"failing": failing_provider}
        registry._initialized = True
        
        # Should not raise, just log the error
        await registry.shutdown()
        
        assert registry._initialized is False


class TestServiceProviderImplementations:
    """Test individual ServiceProvider implementations.
    
    Note: These tests verify that providers work correctly with real implementations.
    Mock patching is done at the point where the module is imported inside the provider methods.
    """
    
    # =========================================================================
    # Test: LocalFileServiceProvider
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_local_file_provider_initializes(self):
        """LocalFileServiceProvider should initialize successfully."""
        # Patch at the import location inside the initialize method
        with patch('src.services.local_file_service.LocalFileService') as mock_class:
            mock_service = MagicMock()
            mock_class.return_value = mock_service
            
            provider = LocalFileServiceProvider()
            await provider.initialize()
            
            # Verify service was created
            assert provider._service is not None
    
    @pytest.mark.asyncio
    async def test_local_file_provider_initializes_real(self):
        """LocalFileServiceProvider initializes with real LocalFileService."""
        provider = LocalFileServiceProvider()
        await provider.initialize()
        
        service = provider.get_service()
        assert service is not None
    
    # =========================================================================
    # Test: GeminiAIProvider
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_gemini_provider_initializes(self):
        """GeminiAIProvider should initialize successfully (may have no API key)."""
        provider = GeminiAIProvider()
        await provider.initialize()
        
        service = provider.get_service()
        assert service is not None
    
    # =========================================================================
    # Test: ResumeServiceProvider
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_resume_provider_initializes_with_file_service(self):
        """ResumeServiceProvider should initialize with file service dependency."""
        mock_file_service = MagicMock()
        
        # Use real initialization - repository_factory will return None if DB unavailable
        provider = ResumeServiceProvider(mock_file_service)
        await provider.initialize()
        
        service = provider.get_service()
        assert service is not None
        assert provider.file_service == mock_file_service
    
    # =========================================================================
    # Test: ApplicationServiceProvider
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_application_provider_initializes(self):
        """ApplicationServiceProvider should initialize successfully."""
        mock_file_service = MagicMock()
        
        provider = ApplicationServiceProvider(mock_file_service)
        await provider.initialize()
        
        service = provider.get_service()
        assert service is not None
        assert provider.file_service == mock_file_service
    
    # =========================================================================
    # Test: CoverLetterServiceProvider
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_cover_letter_provider_initializes(self):
        """CoverLetterServiceProvider should initialize successfully."""
        mock_ai_service = MagicMock()
        
        provider = CoverLetterServiceProvider(mock_ai_service)
        await provider.initialize()
        
        service = provider.get_service()
        assert service is not None
        assert provider.ai_service == mock_ai_service
    
    # =========================================================================
    # Test: JobSearchServiceProvider
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_job_search_provider_initializes(self):
        """JobSearchServiceProvider should initialize successfully."""
        provider = JobSearchServiceProvider()
        await provider.initialize()
        
        service = provider.get_service()
        assert service is not None
    
    # =========================================================================
    # Test: JobApplicationServiceProvider
    # =========================================================================
    
    @pytest.mark.asyncio
    async def test_job_application_provider_initializes(self):
        """JobApplicationServiceProvider should initialize successfully."""
        provider = JobApplicationServiceProvider()
        await provider.initialize()
        
        service = provider.get_service()
        assert service is not None


class TestDependencyInjection:
    """Test proper dependency injection patterns."""
    
    @pytest.mark.asyncio
    async def test_services_receive_correct_dependencies(self):
        """Verify services receive their correct dependencies."""
        mock_file_service = MagicMock()
        mock_ai_service = MagicMock()
        
        # Test ResumeServiceProvider dependency injection
        resume_provider = ResumeServiceProvider(mock_file_service)
        assert resume_provider.file_service == mock_file_service
        
        # Test ApplicationServiceProvider dependency injection
        app_provider = ApplicationServiceProvider(mock_file_service)
        assert app_provider.file_service == mock_file_service
        
        # Test CoverLetterServiceProvider dependency injection
        cover_provider = CoverLetterServiceProvider(mock_ai_service)
        assert cover_provider.ai_service == mock_ai_service
    
    @pytest.mark.asyncio
    async def test_providers_are_independent(self):
        """Verify providers don't share state inappropriately."""
        registry1 = ServiceRegistry()
        registry2 = ServiceRegistry()
        
        mock_provider = MockServiceProvider("test")
        registry1.register_service("test", mock_provider)
        
        assert "test" in registry1._services
        assert "test" not in registry2._services
