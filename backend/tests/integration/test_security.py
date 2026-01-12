import pytest
import sys
from unittest.mock import MagicMock

# Mock magic module before importing anything that uses it
sys.modules["magic"] = MagicMock()

from httpx import AsyncClient, ASGITransport
from src.api.app import create_app
from src.utils.file_security import FileSecurityService
from src.utils.sanitization import sanitize_input
from fastapi import UploadFile
import io
from unittest.mock import patch

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_security_headers(client):
    """Test that security headers are present in responses."""
    response = await client.get("/health")
    assert response.status_code == 200
    
    headers = response.headers
    assert "content-security-policy" in headers
    assert "x-frame-options" in headers
    assert headers["x-frame-options"] == "DENY"
    assert "x-content-type-options" in headers
    assert headers["x-content-type-options"] == "nosniff"
    assert "referrer-policy" in headers

def test_sanitization():
    """Test input sanitization."""
    # Test HTML sanitization
    dirty_html = "<script>alert('xss')</script><b>Bold</b>"
    clean_html = sanitize_input(dirty_html)
    assert "<script>" not in clean_html
    assert "&lt;script&gt;" in clean_html  # Should be escaped or stripped depending on implementation
    
    # Test dictionary sanitization
    dirty_dict = {"key": "<script>alert('xss')</script>", "safe": "value"}
    clean_dict = sanitize_input(dirty_dict)
    assert "<script>" not in clean_dict["key"]
    assert clean_dict["safe"] == "value"

@pytest.mark.asyncio
async def test_file_security_validation():
    """Test file security validation."""
    # Case 1: Magic is available (simulated)
    with patch('src.utils.file_security.MAGIC_AVAILABLE', True):
        with patch('magic.Magic') as mock_magic_class:
            mock_instance = MagicMock()
            mock_magic_class.return_value = mock_instance
            
            # Setup for PDF
            mock_instance.from_buffer.return_value = "application/pdf"
            
            pdf_content = b"%PDF-1.4\n..." 
            file = io.BytesIO(pdf_content)
            upload_file = UploadFile(file=file, filename="test.pdf")
            
            # Should pass
            result = await FileSecurityService.validate_file(upload_file, category="document")
            assert result is True
            
            # Setup for Malicious Script
            mock_instance.from_buffer.return_value = "application/x-sh"
            
            script_content = b"#!/bin/bash\n..."
            file = io.BytesIO(script_content)
            upload_file = UploadFile(file=file, filename="malicious.pdf")
            
            # Should fail
            with pytest.raises(Exception) as excinfo:
                await FileSecurityService.validate_file(upload_file, category="document")
            assert excinfo.value.status_code == 415

    # Case 2: Magic is NOT available (fallback)
    with patch('src.utils.file_security.MAGIC_AVAILABLE', False):
        # Valid header
        pdf_content = b"%PDF-1.4\n..." 
        file = io.BytesIO(pdf_content)
        
        # Use MagicMock for UploadFile to avoid setter issues
        upload_file = MagicMock(spec=UploadFile)
        upload_file.file = file
        upload_file.filename = "test.pdf"
        upload_file.content_type = "application/pdf"
        
        result = await FileSecurityService.validate_file(upload_file, category="document")
        assert result is True
        
        # Invalid header
        upload_file.content_type = "application/x-sh"
        with pytest.raises(Exception) as excinfo:
            await FileSecurityService.validate_file(upload_file, category="document")
        assert excinfo.value.status_code == 415
