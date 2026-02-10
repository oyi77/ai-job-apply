# Auto-Apply Model Alignment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Align auto-apply Pydantic schemas and unit tests with the new DB models and API payloads.

**Architecture:** Update Pydantic v2 models in the automation schema module to reflect DB fields and API payloads, then update unit tests to match new request/response shapes. Follow strict TDD: write failing tests first, run to confirm failure, implement minimal schema changes, re-run tests, then refactor if needed.

**Tech Stack:** FastAPI, Pydantic v2, pytest, Python 3.11

---

### Task 1: Update AutoApplyConfig schemas

**Files:**
- Modify: `backend/src/models/automation.py`
- Test: `backend/tests/unit/test_auto_apply_api.py`

**Step 1: Write the failing test**

Update the test payloads and expected fields for config creation and update to use `keywords`, `locations`, `min_salary`, `daily_limit`, `is_active` as optional fields. Ensure response expects `id`, `user_id`, `created_at`, `updated_at` and fields above.

```python
def test_create_config_success(self, client, user, auth_headers):
    payload = {
        "keywords": ["backend", "python"],
        "locations": ["remote"],
        "min_salary": 90000,
        "daily_limit": 10,
        "is_active": True,
    }
    response = client.post("/api/v1/auto-apply/config", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["keywords"] == payload["keywords"]
    assert data["locations"] == payload["locations"]
    assert data["min_salary"] == payload["min_salary"]
    assert data["daily_limit"] == payload["daily_limit"]
    assert data["is_active"] is True
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/unit/test_auto_apply_api.py::TestAutoApplyAPI::test_create_config_success -v`
Expected: FAIL with missing fields or schema validation mismatch.

**Step 3: Write minimal implementation**

Update Pydantic schemas in `backend/src/models/automation.py`:
- `AutoApplyConfigCreate` accepts optional `keywords: list[str] | None`, `locations: list[str] | None`, `min_salary: int | None`, `daily_limit: int | None`, `is_active: bool | None`.
- `AutoApplyConfigUpdate` mirrors the same optional fields.
- `AutoApplyConfig` includes `id`, `user_id`, `keywords`, `locations`, `min_salary`, `daily_limit`, `is_active`, `created_at`, `updated_at`.

```python
class AutoApplyConfigCreate(BaseModel):
    keywords: list[str] | None = None
    locations: list[str] | None = None
    min_salary: int | None = None
    daily_limit: int | None = None
    is_active: bool | None = None
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/unit/test_auto_apply_api.py::TestAutoApplyAPI::test_create_config_success -v`
Expected: PASS

**Step 5: Refactor if needed**

Keep schema naming consistent with current file conventions; no extra validations beyond required fields.

---

### Task 2: Update AutoApplyActivityLog schema

**Files:**
- Modify: `backend/src/models/automation.py`
- Test: `backend/tests/unit/test_auto_apply_api.py`

**Step 1: Write the failing test**

Update any tests asserting activity log response fields to expect:
`cycle_id`, `cycle_start`, `cycle_status`, `jobs_searched`, `jobs_matched`, `jobs_applied`, `applications_successful`, `applications_failed`, `errors`, `screenshots`, `created_at`, `updated_at`.

```python
assert "cycle_id" in data
assert "cycle_start" in data
assert "cycle_status" in data
assert "jobs_searched" in data
assert "jobs_matched" in data
assert "jobs_applied" in data
assert "applications_successful" in data
assert "applications_failed" in data
assert "errors" in data
assert "screenshots" in data
assert "created_at" in data
assert "updated_at" in data
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/unit/test_auto_apply_api.py::TestAutoApplyAPI::<relevant_test_name> -v`
Expected: FAIL with missing fields or mismatched response schema.

**Step 3: Write minimal implementation**

Update `AutoApplyActivityLog` in `backend/src/models/automation.py` to include the fields above with correct optionality and types matching DB models (e.g., `errors: list[str] | None`, `screenshots: list[str] | None`).

```python
class AutoApplyActivityLog(BaseModel):
    cycle_id: str
    cycle_start: datetime
    cycle_status: str
    jobs_searched: int
    jobs_matched: int
    jobs_applied: int
    applications_successful: int
    applications_failed: int
    errors: list[str] | None = None
    screenshots: list[str] | None = None
    created_at: datetime
    updated_at: datetime
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/unit/test_auto_apply_api.py::TestAutoApplyAPI::<relevant_test_name> -v`
Expected: PASS

**Step 5: Refactor if needed**

Align with existing model base classes or config in file; avoid extra validation logic.

---

### Task 3: Verification

**Files:**
- Test: `backend/tests/unit/test_auto_apply_api.py`
- Modify: `backend/src/models/automation.py`

**Step 1: Run targeted tests**

Run: `cd backend && pytest tests/unit/test_auto_apply_api.py::TestAutoApplyAPI::test_create_config_success -v`
Expected: PASS

**Step 2: Run full unit file**

Run: `cd backend && pytest tests/unit/test_auto_apply_api.py -v`
Expected: PASS

**Step 3: Run lsp diagnostics**

Run lsp diagnostics on:
- `backend/src/models/automation.py`
- `backend/tests/unit/test_auto_apply_api.py`
Expected: No errors or warnings.
