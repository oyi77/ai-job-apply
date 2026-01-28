# Learnings from fixing JobSearch.test.tsx

## Issues Identified
1.  **ResizeObserver Error**: The `JobSearch` component uses `Modal` (likely Headless UI) which relies on `ResizeObserver`. This was missing in the test environment (JSDOM), causing `TypeError: ... is not a constructor`.
2.  **Missing Search Input**: Two tests (`handles apply flow` and `handles save job`) failed because they called `searchAndClick` without first typing into the search input. The component's `handleSearch` function has a check `if (searchQuery.trim())`, so it skips the API call if the search box is empty. This resulted in no jobs being rendered and `findByText` failing.
3.  **Mock Warnings**: `vi.fn()` without implementation can cause warnings or issues if the code expects a Promise (e.g., `useQuery` fn).
4.  **Multiple Elements Error**: The text "We are looking for a software engineer..." appeared both in the job list (truncated) and the job detail modal. `getByText` failed because it found multiple elements.

## Solutions
1.  **Polyfills**: Added `ResizeObserver` and `IntersectionObserver` mocks at the top of the test file.
2.  **Test Updates**: Ensured `user.type(...)` is called before clicking search in all tests.
3.  **Scoped Queries**: Used `within(modal).getByText(...)` to ensure we are asserting on the modal content, not the background list.
4.  **Robustness**: Used `mockResolvedValue` for default mocks to ensure they return Promises.
