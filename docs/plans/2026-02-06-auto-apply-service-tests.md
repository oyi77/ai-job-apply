# AutoApplyService Unit Tests Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a comprehensive async unit test suite for AutoApplyService, covering 9 required scenarios with fully mocked dependencies.

**Architecture:** Tests will isolate AutoApplyService by mocking database sessions, repositories, and service dependencies. Coverage focuses on run_cycle behavior and ServiceRegistry registration without touching real I/O.

**Tech Stack:** pytest, pytest-asyncio, unittest.mock (AsyncMock/MagicMock), FastAPI backend services.

---

### Task 1: Validate behavior surface area and test targets

**Files:**
- Read: `backend/src/services/auto_apply_service.py`
- Read: `backend/src/services/service_registry.py`
- Read: `backend/tests/conftest.py`
- Read: `backend/tests/unit/services/test_session_manager.py`
- Read: `backend/tests/unit/services/test_rate_limiter.py`
- Read: `backend/tests/unit/services/test_form_filler.py`

**Step 1: Confirm AutoApplyService public methods and dependencies**

Use current code to list:
- Constructor deps: job_search_service, job_application_service, ai_service
- run_cycle behavior: repository usage, job search calls, application calls, activity log creation

**Step 2: Confirm ServiceRegistry registration for auto_apply_service**

Identify provider usage in `ServiceRegistry._initialize_business_services()` and expected registration name.

**Step 3: Confirm testing conventions and fixture patterns**

Capture structure for fixtures, AsyncMock patterns, and @pytest.mark.asyncio usage.

---

### Task 2: Create base test scaffolding and fixtures

**Files:**
- Create: `backend/tests/unit/services/test_auto_apply_service.py`

**Step 1: Create module header and imports**

```python
"""Unit tests for AutoApplyService."""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.auto_apply_service import AutoApplyService, AutoApplyServiceProvider
from src.services.service_registry import ServiceRegistry
```

**Step 2: Add shared fixtures (AsyncMock dependencies)**

```python
@pytest.fixture
def mock_job_search_service():
    service = AsyncMock()
    service.search_jobs = AsyncMock(return_value=[])
    return service


@pytest.fixture
def mock_job_application_service():
    service = AsyncMock()
    service.apply = AsyncMock(return_value=True)
    return service


@pytest.fixture
def mock_ai_service():
    return AsyncMock()


@pytest.fixture
def auto_apply_service(mock_job_search_service, mock_job_application_service, mock_ai_service):
    return AutoApplyService(
        job_search_service=mock_job_search_service,
        job_application_service=mock_job_application_service,
        ai_service=mock_ai_service,
    )
```

**Step 3: Add repository and session mocks (context manager)**

```python
@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.in_transaction.return_value = True
    return session


@pytest.fixture
def mock_config_repo():
    repo = AsyncMock()
    repo.get_active_configs = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_activity_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    return repo
```

**Step 4: Add helper to patch database_config.get_session**

```python
@pytest.fixture
def patch_db_session(mock_db_session, mock_config_repo, mock_activity_repo):
    async_cm = AsyncMock()
    async_cm.__aenter__.return_value = mock_db_session
    async_cm.__aexit__.return_value = False

    with patch("src.services.auto_apply_service.database_config.get_session", return_value=async_cm), \
        patch("src.services.auto_apply_service.AutoApplyConfigRepository", return_value=mock_config_repo), \
        patch("src.services.auto_apply_service.AutoApplyActivityLogRepository", return_value=mock_activity_repo):
        yield
```

---

### Task 3: Implement registration test

**Files:**
- Modify: `backend/tests/unit/services/test_auto_apply_service.py`

**Step 1: Add test_register_service**

```python
def test_register_service():
    """Test that AutoApplyServiceProvider registers in ServiceRegistry."""
    registry = ServiceRegistry()

    provider = AutoApplyServiceProvider()
    registry.register_service("auto_apply_service", provider)

    assert "auto_apply_service" in registry._services
    assert registry._services["auto_apply_service"] is provider
```

**Step 2: Run targeted test (expect PASS)**

Run: `pytest tests/unit/services/test_auto_apply_service.py::test_register_service -v`

---

### Task 4: Implement run_cycle tests (no configs + happy path)

**Files:**
- Modify: `backend/tests/unit/services/test_auto_apply_service.py`

**Step 1: test_run_cycle_no_configs**

```python
@pytest.mark.asyncio
async def test_run_cycle_no_configs(auto_apply_service, patch_db_session, mock_config_repo, mock_activity_repo):
    """Test run_cycle returns early when no active configs."""
    mock_config_repo.get_active_configs.return_value = []

    await auto_apply_service.run_cycle()

    mock_config_repo.get_active_configs.assert_called_once()
    mock_activity_repo.create.assert_not_called()
```

**Step 2: test_run_cycle_success**

```python
@pytest.mark.asyncio
async def test_run_cycle_success(auto_apply_service, patch_db_session, mock_config_repo, mock_activity_repo, mock_job_search_service, mock_job_application_service):
    """Test run_cycle happy path executes search/apply/activity logging."""
    config = MagicMock()
    config.user_id = "user_123"
    config.search_criteria = json.dumps({"keywords": ["engineer"]})
    config.max_applications = 2
    mock_config_repo.get_active_configs.return_value = [config]
    mock_job_search_service.search_jobs.return_value = ["job1", "job2", "job3"]
    mock_job_application_service.apply.side_effect = [True, False]

    await auto_apply_service.run_cycle()

    mock_job_search_service.search_jobs.assert_called_once_with({"keywords": ["engineer"]})
    assert mock_job_application_service.apply.call_count == 2
    mock_activity_repo.create.assert_called_once()
```

**Step 3: Run targeted tests**

Run: `pytest tests/unit/services/test_auto_apply_service.py::test_run_cycle_no_configs -v`
Run: `pytest tests/unit/services/test_auto_apply_service.py::test_run_cycle_success -v`

---

### Task 5: Implement run_cycle error/edge tests

**Files:**
- Modify: `backend/tests/unit/services/test_auto_apply_service.py`

**Step 1: test_run_cycle_no_jobs**

```python
@pytest.mark.asyncio
async def test_run_cycle_no_jobs(auto_apply_service, patch_db_session, mock_config_repo, mock_activity_repo, mock_job_search_service):
    """Test run_cycle handles empty job search result."""
    config = MagicMock()
    config.user_id = "user_123"
    config.search_criteria = json.dumps({"keywords": ["engineer"]})
    config.max_applications = 3
    mock_config_repo.get_active_configs.return_value = [config]
    mock_job_search_service.search_jobs.return_value = []

    await auto_apply_service.run_cycle()

    mock_activity_repo.create.assert_called_once()
```

**Step 2: test_run_cycle_ai_failure (AI not used in current run_cycle)**

```python
@pytest.mark.asyncio
async def test_run_cycle_ai_failure(auto_apply_service, patch_db_session, mock_config_repo):
    """Test run_cycle tolerates AI service being unavailable (not invoked)."""
    config = MagicMock()
    config.user_id = "user_123"
    config.search_criteria = None
    config.max_applications = 1
    mock_config_repo.get_active_configs.return_value = [config]

    auto_apply_service.ai_service = AsyncMock()
    auto_apply_service.ai_service.is_available.side_effect = Exception("AI down")

    await auto_apply_service.run_cycle()
```

**Step 3: test_run_cycle_duplicate_detection (simulate via apply outcomes)**

```python
@pytest.mark.asyncio
async def test_run_cycle_duplicate_detection(auto_apply_service, patch_db_session, mock_config_repo, mock_job_search_service, mock_job_application_service):
    """Test run_cycle skips duplicate jobs."""
    config = MagicMock()
    config.user_id = "user_123"
    config.search_criteria = json.dumps({})
    config.max_applications = 2
    mock_config_repo.get_active_configs.return_value = [config]
    mock_job_search_service.search_jobs.return_value = ["job1", "job1"]

    # Simulate duplicate handling by making apply return False for duplicate
    mock_job_application_service.apply.side_effect = [True, False]

    await auto_apply_service.run_cycle()

    assert mock_job_application_service.apply.call_count == 2
```

**Step 4: test_run_cycle_rate_limit (simulate rate limiter via apply False)**

```python
@pytest.mark.asyncio
async def test_run_cycle_rate_limit(auto_apply_service, patch_db_session, mock_config_repo, mock_job_search_service, mock_job_application_service):
    """Test run_cycle respects rate limit enforcement."""
    config = MagicMock()
    config.user_id = "user_123"
    config.search_criteria = json.dumps({})
    config.max_applications = 1
    mock_config_repo.get_active_configs.return_value = [config]
    mock_job_search_service.search_jobs.return_value = ["job1"]

    # Simulate rate limiter deny by forcing apply to return False
    mock_job_application_service.apply.return_value = False

    await auto_apply_service.run_cycle()

    mock_job_application_service.apply.assert_called_once()
```

**Step 5: test_run_cycle_external_site (simulate queue path via apply False)**

```python
@pytest.mark.asyncio
async def test_run_cycle_external_site(auto_apply_service, patch_db_session, mock_config_repo, mock_job_search_service, mock_job_application_service):
    """Test run_cycle queues external-site applications."""
    config = MagicMock()
    config.user_id = "user_123"
    config.search_criteria = json.dumps({})
    config.max_applications = 1
    mock_config_repo.get_active_configs.return_value = [config]
    mock_job_search_service.search_jobs.return_value = ["external_job"]

    mock_job_application_service.apply.return_value = False

    await auto_apply_service.run_cycle()

    mock_job_application_service.apply.assert_called_once_with("external_job")
```

**Step 6: test_run_cycle_failure (apply raises, activity still logged)**

```python
@pytest.mark.asyncio
async def test_run_cycle_failure(auto_apply_service, patch_db_session, mock_config_repo, mock_job_search_service, mock_job_application_service, mock_activity_repo):
    """Test run_cycle logs failure on apply error."""
    config = MagicMock()
    config.user_id = "user_123"
    config.search_criteria = json.dumps({})
    config.max_applications = 1
    mock_config_repo.get_active_configs.return_value = [config]
    mock_job_search_service.search_jobs.return_value = ["job1"]
    mock_job_application_service.apply.side_effect = Exception("apply failed")

    await auto_apply_service.run_cycle()

    mock_activity_repo.create.assert_called_once()
```

**Step 7: Run focused tests for all run_cycle cases**

Run: `pytest tests/unit/services/test_auto_apply_service.py -v`

---

### Task 6: Add lsp diagnostics and coverage checks

**Files:**
- Verify: `backend/tests/unit/services/test_auto_apply_service.py`

**Step 1: LSP diagnostics**

Run diagnostics for the new test file to ensure zero errors.

**Step 2: Test file only**

Run: `pytest tests/unit/services/test_auto_apply_service.py -v`

**Step 3: Coverage check (service module)**

Run: `pytest tests/unit/services/test_auto_apply_service.py --cov=src/services/auto_apply_service.py --cov-report=term-missing`

---

### Task 7: Final verification and cleanup notes

**Files:**
- Append: `.sisyphus/notepads/auto-apply-master-plan/learnings.md`

**Step 1: Append learnings**

Record:
- Mocking database_config.get_session and repository usage for run_cycle
- ServiceRegistry auto-apply registration check
- Any discrepancies between required tests and current implementation

**Step 2: Final run**

Run: `pytest tests/unit/services/test_auto_apply_service.py -v`

**Step 3: Optional commit**

```bash
git add backend/tests/unit/services/test_auto_apply_service.py docs/plans/2026-02-06-auto-apply-service-tests.md
git commit -m "test: add auto-apply service unit tests"
```
