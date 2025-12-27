# Adding Tags to Vibe Kanban

Unfortunately, Vibe Kanban's MCP server doesn't currently have an API endpoint for creating tags programmatically. Tags need to be added manually through the Vibe Kanban UI.

However, I've prepared all 60 tags in a structured format for easy import.

## Quick Import Method

### Option 1: Manual Import (Recommended)

1. **Open Vibe Kanban** → Settings → Tags
2. **Click "+ Add Tag"**
3. **For each tag in `vibe-kanban-tags.json`:**
   - Tag Name: Copy the `tag_name` (e.g., `@openspec_review`)
   - Content: Copy the `content` field
   - Click Save
   - Repeat for all 60 tags

### Option 2: Use the Import Guide

I've created `scripts/vibe-kanban-tags-import.md` with all tags formatted for easy copying. Each tag is clearly labeled with its name and content.

## Tag Categories

The tags are organized into these categories:

1. **Development Workflow** (5 tags) - OpenSpec integration
2. **Code Quality** (5 tags) - Testing, refactoring, documentation
3. **Testing** (4 tags) - Unit, integration, E2E, performance
4. **Database** (4 tags) - Migrations, indexing, optimization
5. **API Development** (5 tags) - Endpoints, documentation, security
6. **Frontend Development** (5 tags) - Components, state, forms
7. **Security** (5 tags) - Audit, headers, authentication
8. **Performance** (4 tags) - Optimization, caching, monitoring
9. **Infrastructure** (4 tags) - Docker, CI/CD, deployment
10. **Documentation** (4 tags) - README, API docs, architecture
11. **Bug Fixes** (3 tags) - Analysis, fixing, testing
12. **Feature Development** (3 tags) - Implementation, testing, docs
13. **Code Quality & Maintenance** (3 tags) - Technical debt, cleanup
14. **OpenSpec Integration** (4 tags) - Proposal, implementation, sync
15. **Analytics & Reporting** (2 tags) - Analytics, reporting
16. **AI & ML** (2 tags) - AI integration, optimization
17. **Job Search** (2 tags) - Integration, matching

**Total: 60 tag templates**

## Priority Order for Import

If you want to import in priority order:

### High Priority (Import First)
- `@openspec_link` - Required for OpenSpec tasks
- `@openspec_review` - Required workflow step
- `@add_unit_tests` - Essential for quality
- `@test_coverage` - Quality gate
- `@code_review` - Code quality
- `@security_audit` - Security requirement

### Medium Priority
- All other tags based on your immediate needs

## Usage After Import

Once tags are imported, you can use them in task descriptions:

```
@openspec_link
@add_unit_tests
@code_review
```

The tag content will automatically be inserted into your task description when Vibe Kanban processes it.

## Files Provided

1. **`scripts/vibe-kanban-tags.json`** - JSON format with all 60 tags (structured data)
2. **`scripts/vibe-kanban-tags-import.md`** - Human-readable format for manual import
3. **`scripts/workflow-tags.md`** - Original tag documentation with examples

## Future Enhancement

If Vibe Kanban adds a tag management API endpoint in the future, we can create an automated import script. For now, manual import is required but the tags are prepared in a structured format to make it easy.

