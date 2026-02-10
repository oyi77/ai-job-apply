# Issues

## TestDeleteUser Test Fixes (COMPLETED)
Fixed 3 failing tests in `backend/tests/unit/test_auth_service.py`:

1. **test_delete_user_success**: Added `password` argument to `delete_user()` call, mocked `_verify_password` method
2. **test_delete_user_not_found**: Added `password` argument to `delete_user()` call
3. **test_logout_wrong_user**: Corrected test expectation - implementation returns `False` (not `True`) for security when user_id mismatch

**Root cause**: Tests didn't match implementation signature - `delete_user(user_id, password)` requires 2 args.

**Result**: All 3 TestDeleteUser tests now PASS (previously 5 auth tests failing, now 2 remaining in other test classes).

---

- Reminder callbacks only mark `sent` when notification delivery succeeds; in dev without email config, rely on scheduler logs (`Job <id> executed successfully`) to confirm execution.
