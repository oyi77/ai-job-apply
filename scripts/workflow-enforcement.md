# Workflow Enforcement: OpenSpec ↔ Vibe Kanban Integration

## Overview

This workflow enforcement system ensures that all development work follows a structured process integrating OpenSpec proposals with Vibe Kanban task management.

## Workflow Rules

### 1. Proposal Creation (OpenSpec)

**BEFORE** starting any new feature or significant change:

1. ✅ **Create OpenSpec Proposal**
   - Create proposal in `openspec/changes/<change-id>/`
   - Include: `proposal.md`, `tasks.md`, optional `design.md`
   - Run: `openspec validate <change-id> --strict`
   - Get approval before starting implementation

2. ✅ **Create Vibe Kanban Task**
   - Use script: `python scripts/workflow-orchestrator.py --summary`
   - Create main task in Vibe Kanban from OpenSpec proposal
   - Include tag: `@openspec_link`

3. ✅ **Create Subtasks from tasks.md**
   - Use script to parse `tasks.md` from OpenSpec
   - Create subtasks in Vibe Kanban for each major section
   - Link subtasks to parent task

### 2. Implementation (OpenSpec + Vibe Kanban)

**DURING** implementation:

1. ✅ **Review OpenSpec Documents**
   - Read `proposal.md` - understand what's being built
   - Read `design.md` (if exists) - review technical decisions
   - Read `tasks.md` - get implementation checklist
   - Use tag: `@openspec_review`

2. ✅ **Follow Tasks Checklist**
   - Complete tasks from `tasks.md` sequentially
   - Update Vibe Kanban subtask status as you complete
   - Mark tasks in `tasks.md` as `- [x]` when done

3. ✅ **Use Tag Templates**
   - Add relevant tags to Vibe Kanban tasks
   - Use tags from `workflow-tags.md`
   - Tags help with consistency and automation

4. ✅ **Update Status**
   - Update `STATUS.md` in OpenSpec as you progress
   - Sync Vibe Kanban task status with OpenSpec status
   - Keep both in sync

### 3. Completion (OpenSpec + Vibe Kanban)

**AFTER** implementation:

1. ✅ **Verify Completion**
   - All tasks in `tasks.md` marked as `- [x]`
   - All Vibe Kanban subtasks completed
   - All requirements from proposal met

2. ✅ **Archive OpenSpec Change**
   - Move to `openspec/changes/archive/YYYY-MM-DD-<change-id>/`
   - Update specs if capabilities changed
   - Run: `openspec archive <change-id> --yes`

3. ✅ **Close Vibe Kanban Task**
   - Mark main task as "done"
   - Ensure all subtasks completed
   - Add completion notes

## Automation Scripts

### Workflow Orchestrator

```bash
# Print workflow summary
python scripts/workflow-orchestrator.py --summary

# Generate workflow report (JSON)
python scripts/workflow-orchestrator.py --report

# Generate task descriptions for Vibe Kanban
python scripts/workflow-orchestrator.py --project-id <project-id>
```

### Integration Script (TODO)

Create a script that:
1. Reads OpenSpec changes
2. Creates/updates Vibe Kanban tasks
3. Creates subtasks from tasks.md
4. Syncs status between OpenSpec and Vibe Kanban
5. Links design documents

## Enforcement Checklist

### Before Starting Work

- [ ] OpenSpec proposal exists and is approved
- [ ] Vibe Kanban task created from proposal
- [ ] Subtasks created from tasks.md
- [ ] Design document reviewed (if exists)
- [ ] All tags applied to task
- [ ] OpenSpec validation passed

### During Implementation

- [ ] Following tasks.md checklist
- [ ] Updating Vibe Kanban subtasks as completed
- [ ] Marking tasks.md items as done
- [ ] Updating STATUS.md periodically
- [ ] Using appropriate tags

### After Completion

- [ ] All tasks.md items completed
- [ ] All Vibe Kanban subtasks completed
- [ ] STATUS.md updated to 100%
- [ ] OpenSpec change archived
- [ ] Vibe Kanban task marked done
- [ ] Documentation updated

## Tag Usage Guidelines

### Required Tags

- `@openspec_link` - Always include in tasks created from OpenSpec
- `@openspec_review` - When reviewing OpenSpec documents
- `@openspec_tasks` - When creating subtasks from tasks.md

### Context-Specific Tags

- **New Feature**: `@feature_implementation`, `@feature_testing`, `@feature_documentation`
- **Bug Fix**: `@bug_analysis`, `@bug_fix`, `@bug_testing`
- **Refactoring**: `@code_refactoring`, `@technical_debt`
- **Testing**: `@add_unit_tests`, `@test_coverage`, `@test_e2e`
- **Security**: `@security_audit`, `@security_headers`, `@input_validation`
- **Performance**: `@performance_optimization`, `@caching`, `@database_optimization`

## Workflow Examples

### Example 1: New Feature

```
1. Create OpenSpec proposal: openspec/changes/add-email-notifications/
   - proposal.md: Why, what changes, impact
   - tasks.md: Implementation checklist
   - design.md: Technical decisions (if needed)

2. Validate: openspec validate add-email-notifications --strict

3. Create Vibe Kanban task:
   - Title: "Add Email Notification System"
   - Description: Generated from proposal.md
   - Tags: @openspec_link, @feature_implementation, @api_endpoint

4. Create subtasks from tasks.md:
   - Subtask: "1. Email Service Setup" (from tasks.md section 1)
   - Subtask: "2. Notification Templates" (from tasks.md section 2)
   - etc.

5. Implement following tasks.md checklist

6. Update as you go:
   - Mark tasks.md items as done
   - Update Vibe Kanban subtask status
   - Update STATUS.md

7. Complete:
   - Archive OpenSpec change
   - Mark Vibe Kanban task as done
```

### Example 2: Bug Fix

```
1. Create OpenSpec proposal (if significant):
   - openspec/changes/fix-email-delivery-issue/
   - proposal.md: Problem description, solution, impact

2. Create Vibe Kanban task:
   - Title: "Fix Email Delivery Issue"
   - Tags: @bug_analysis, @bug_fix, @bug_testing

3. Follow bug fix workflow:
   - Analyze root cause
   - Implement fix
   - Add tests
   - Verify fix

4. Complete and archive
```

## CI/CD Integration

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check if OpenSpec proposal exists for new features
# Verify tasks.md structure
# Check tag usage in commit messages
```

### GitHub Actions Workflow

```yaml
name: Workflow Enforcement

on:
  pull_request:
    branches: [main, develop]

jobs:
  openspec-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate OpenSpec
        run: |
          openspec validate --strict
      - name: Check Vibe Kanban Integration
        run: |
          python scripts/workflow-orchestrator.py --report
```

## Benefits

1. **Consistency**: All work follows same process
2. **Traceability**: Link between OpenSpec and Vibe Kanban
3. **Automation**: Scripts reduce manual work
4. **Quality**: Enforces review and validation
5. **Documentation**: Automatic documentation generation
6. **Collaboration**: Clear workflow for team members

## Maintenance

### Weekly Review

- Review OpenSpec changes without Vibe Kanban tasks
- Sync status between OpenSpec and Vibe Kanban
- Update tag templates as needed
- Review workflow effectiveness

### Monthly Review

- Analyze workflow metrics
- Identify bottlenecks
- Improve automation scripts
- Update documentation

## Troubleshooting

### OpenSpec Change Without Vibe Kanban Task

```bash
# Find orphaned changes
python scripts/workflow-orchestrator.py --summary

# Create missing tasks manually or via script
```

### Vibe Kanban Task Without OpenSpec

- Determine if OpenSpec proposal needed
- Create proposal if significant change
- Link to existing proposal if appropriate

### Status Out of Sync

```bash
# Generate sync report
python scripts/workflow-orchestrator.py --report

# Manually sync or use automation script
```

## Future Enhancements

1. **Automated Task Creation**: Script to create Vibe Kanban tasks from OpenSpec
2. **Status Sync**: Automatically sync status between OpenSpec and Vibe Kanban
3. **Notification System**: Notify when tasks need attention
4. **Metrics Dashboard**: Track workflow metrics and effectiveness
5. **Integration API**: Direct API integration between OpenSpec and Vibe Kanban

