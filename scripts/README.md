# Workflow Orchestration Scripts

This directory contains scripts for enforcing workflow between OpenSpec and Vibe Kanban.

## Scripts

### `workflow-orchestrator.py`

Main orchestration script that integrates OpenSpec proposals with Vibe Kanban task management.

**Usage:**
```bash
# Print workflow summary
python scripts/workflow-orchestrator.py --summary

# Generate workflow report (JSON)
python scripts/workflow-orchestrator.py --report

# Generate task descriptions for specific project
python scripts/workflow-orchestrator.py --project-id <vibe-kanban-project-id>
```

**Features:**
- Discovers all OpenSpec changes
- Parses proposal.md, tasks.md, and design.md
- Generates Vibe Kanban task descriptions
- Creates subtasks from tasks.md
- Generates workflow reports

### `workflow-tags.md`

Tag templates for Vibe Kanban tasks. Copy tags and use in task descriptions.

**Usage:**
1. Copy tag name (e.g., `@openspec_review`)
2. Paste in Vibe Kanban task description
3. Tag content will be inserted automatically

**Categories:**
- Development Workflow
- Code Quality
- Testing
- Database
- API Development
- Frontend Development
- Security
- Performance
- Infrastructure
- Documentation
- Bug Fixes
- Feature Development
- OpenSpec Integration

### `workflow-enforcement.md`

Complete workflow enforcement rules and guidelines.

**Key Rules:**
1. All OpenSpec changes MUST have Vibe Kanban tasks
2. Create subtasks from tasks.md
3. Link to design documents
4. Use workflow tags
5. Sync status between OpenSpec and Vibe Kanban

## Workflow Process

### 1. Create OpenSpec Proposal

```bash
# Create proposal
mkdir openspec/changes/add-new-feature/
# Add proposal.md, tasks.md, optional design.md

# Validate
openspec validate add-new-feature --strict
```

### 2. Create Vibe Kanban Task

```bash
# Generate task description
python scripts/workflow-orchestrator.py --summary

# Copy generated description
# Create task in Vibe Kanban
# Add tags: @openspec_link, @openspec_review
```

### 3. Create Subtasks

```bash
# Script will parse tasks.md and generate subtasks
# Create subtasks in Vibe Kanban manually or via automation
```

### 4. Implement

- Follow tasks.md checklist
- Update Vibe Kanban subtasks as you complete
- Mark tasks.md items as done
- Keep STATUS.md in sync

### 5. Complete

- Archive OpenSpec change
- Mark Vibe Kanban task as done
- Update documentation

## Integration Examples

### Example: Creating Task from OpenSpec

```python
from scripts.workflow_orchestrator import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()
changes = orchestrator.discover_changes()

for change in changes:
    description = orchestrator.generate_vibe_kanban_task_description(change)
    metadata = orchestrator.generate_task_metadata(change)
    subtasks = orchestrator.generate_subtasks_from_tasks(change)
    
    # Use description, metadata, subtasks to create Vibe Kanban task
```

## Tag Usage

### Required Tags

- `@openspec_link` - Always include
- `@openspec_review` - When reviewing documents
- `@openspec_tasks` - When creating subtasks

### Common Tag Combinations

**New Feature:**
```
@openspec_link
@openspec_review
@feature_implementation
@add_unit_tests
@api_documentation
```

**Bug Fix:**
```
@bug_analysis
@bug_fix
@bug_testing
@code_review
```

**Refactoring:**
```
@code_refactoring
@technical_debt
@add_type_hints
@test_coverage
```

## Future Enhancements

1. **Automated Task Creation**: Direct API integration with Vibe Kanban
2. **Status Sync**: Automatic sync between OpenSpec and Vibe Kanban
3. **Notification System**: Alert when tasks need attention
4. **Metrics Dashboard**: Track workflow effectiveness
5. **GitHub Actions Integration**: Automated workflow checks in CI/CD

## Troubleshooting

### OpenSpec Change Without Vibe Kanban Task

```bash
python scripts/workflow-orchestrator.py --summary
# Review output, create missing tasks
```

### Status Out of Sync

```bash
python scripts/workflow-orchestrator.py --report
# Review report, manually sync or automate
```

### Missing Tags

Refer to `workflow-tags.md` for complete list of available tags.

