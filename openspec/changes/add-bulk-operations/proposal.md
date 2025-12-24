# Change: Add Bulk Operations

## Why

Users managing many applications need bulk operations for efficiency:
- Bulk status updates
- Bulk deletion
- Bulk export
- Bulk tagging/categorization

PRD mentions bulk operations as future (FR-9.6). Improves user experience for power users.

## What Changes

### Backend
- **Bulk Update Endpoint**: Update multiple applications at once
- **Bulk Delete Endpoint**: Delete multiple applications
- **Bulk Export**: Export multiple applications
- **Bulk Validation**: Validate bulk operations
- **Transaction Management**: Ensure atomicity

### Frontend
- **Bulk Selection UI**: Checkbox selection for items
- **Bulk Actions Menu**: Actions available for selected items
- **Bulk Operation Feedback**: Progress and results display

## Impact

- **Affected specs**: application management, user experience
- **Affected code**:
  - `backend/src/api/v1/applications.py` - Add bulk endpoints
  - `backend/src/services/application_service.py` - Add bulk methods
  - `frontend/src/pages/Applications.tsx` - Add bulk selection UI
- **Breaking changes**: None
- **Database**: Transaction support needed

## Success Criteria

- Users can select multiple applications
- Users can perform bulk operations
- Bulk operations are atomic
- Progress feedback provided
- Error handling for partial failures

