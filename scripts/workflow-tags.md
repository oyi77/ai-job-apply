# Vibe Kanban Tag Templates

These tag templates can be imported into Vibe Kanban for use in task descriptions.

## Usage

1. Copy the tag name (with @ symbol)
2. Use in task descriptions: `@tag_name`
3. The tag content will be inserted automatically

## Tag Templates

### Development Workflow

#### @openspec_review
```
Review OpenSpec proposal, design document, and tasks.md before starting implementation. Ensure all requirements are understood and approved.
```

#### @openspec_validate
```
Run `openspec validate <change-id> --strict` to ensure the OpenSpec proposal is valid before implementation.
```

#### @openspec_tasks
```
Break down implementation into subtasks based on tasks.md from OpenSpec. Each major section should become a subtask.
```

#### @openspec_design
```
Review design.md document (if exists) for technical decisions, architecture patterns, and implementation guidelines before coding.
```

#### @openspec_link
```
Link this Vibe Kanban task to OpenSpec proposal: openspec/changes/<change-id>/proposal.md. Include link in task description.
```

### Code Quality

#### @add_unit_tests
```
Write unit tests to improve code coverage and ensure reliability. Target 95%+ coverage for new code. Use pytest with async support.
```

#### @add_integration_tests
```
Write integration tests for API endpoints and service interactions. Test complete workflows end-to-end.
```

#### @code_review
```
Perform code review focusing on: SOLID principles, type safety, error handling, performance, security, and documentation.
```

#### @code_refactoring
```
Improve code structure and maintainability without changing functionality. Follow DRY principles and eliminate technical debt.
```

#### @add_type_hints
```
Add comprehensive type hints to all functions, methods, and classes. Ensure 100% type coverage. Use mypy for validation.
```

#### @add_docstrings
```
Add Google-style docstrings to all public APIs, classes, and functions. Include parameter descriptions and return types.
```

### Testing

#### @test_coverage
```
Ensure test coverage meets 95%+ target. Add missing tests for edge cases, error scenarios, and boundary conditions.
```

#### @test_performance
```
Add performance tests to ensure API response times < 500ms, database queries < 100ms, and frontend load < 2.5s.
```

#### @test_security
```
Add security tests for authentication, authorization, input validation, SQL injection prevention, and XSS protection.
```

#### @test_e2e
```
Add end-to-end tests using Playwright or Cypress for critical user workflows: register, login, create application, etc.
```

### Database

#### @database_migration
```
Create Alembic migration for schema changes. Test migration up and down. Ensure data integrity and backward compatibility.
```

#### @database_indexing
```
Add database indexes for frequently queried fields, foreign keys, and composite keys to optimize query performance.
```

#### @database_optimization
```
Optimize database queries: eliminate N+1 problems, use selectinload for relationships, implement query result caching.
```

#### @database_backup
```
Implement database backup strategy with automated backups, retention policies, and recovery procedures.
```

### API Development

#### @api_endpoint
```
Create new API endpoint with: request validation (Pydantic), response formatting, error handling, authentication, and documentation.
```

#### @api_documentation
```
Add comprehensive OpenAPI/Swagger documentation: endpoint description, request/response examples, error responses, authentication requirements.
```

#### @api_versioning
```
Implement API versioning strategy. Use /api/v1/ prefix. Plan for future version migration and deprecation policy.
```

#### @api_rate_limiting
```
Add rate limiting to API endpoint using slowapi. Configure appropriate limits based on endpoint sensitivity and usage patterns.
```

#### @api_security
```
Implement security measures: input validation, SQL injection prevention, XSS protection, CSRF tokens, and security headers.
```

### Frontend Development

#### @component_development
```
Create React component with TypeScript, proper prop types, accessibility (ARIA labels), responsive design, and error boundaries.
```

#### @state_management
```
Implement state management using Zustand for client state and React Query for server state. Avoid prop drilling.
```

#### @form_validation
```
Implement form validation using React Hook Form with comprehensive validation rules, error messages, and user feedback.
```

#### @responsive_design
```
Ensure component is responsive and mobile-friendly. Use Tailwind CSS responsive utilities. Test on multiple screen sizes.
```

#### @accessibility
```
Ensure component meets WCAG 2.1 AA standards: keyboard navigation, screen reader support, color contrast, ARIA labels.
```

### Security

#### @security_audit
```
Perform security audit: review authentication, authorization, input validation, file upload security, and OWASP Top 10 compliance.
```

#### @security_headers
```
Implement security headers: HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy.
```

#### @authentication
```
Implement authentication: JWT tokens, password hashing (bcrypt), session management, token refresh, and logout functionality.
```

#### @authorization
```
Implement authorization: role-based access control, permission checks, protected routes, and resource-level permissions.
```

#### @input_validation
```
Add comprehensive input validation: type checking, range validation, sanitization, and SQL injection prevention.
```

### Performance

#### @performance_optimization
```
Optimize performance: reduce API response times, optimize database queries, implement caching, and minimize bundle size.
```

#### @caching
```
Implement caching strategy: Redis for API responses, database query results, and session storage. Configure TTLs and invalidation.
```

#### @database_performance
```
Optimize database performance: add indexes, optimize queries, implement connection pooling, and monitor query performance.
```

#### @frontend_performance
```
Optimize frontend performance: code splitting, lazy loading, image optimization, bundle size reduction, and Core Web Vitals.
```

### Infrastructure

#### @docker_setup
```
Create Dockerfile and docker-compose.yml for containerization. Use multi-stage builds, non-root user, and minimal image size.
```

#### @ci_cd_pipeline
```
Set up CI/CD pipeline: GitHub Actions workflow, automated testing, code quality checks, security scanning, and deployment.
```

#### @monitoring
```
Implement monitoring: APM integration, error tracking (Sentry), log aggregation, health checks, and performance metrics.
```

#### @deployment
```
Set up production deployment: environment configuration, database setup, SSL/TLS certificates, backup strategy, and rollback plan.
```

### Documentation

#### @update_readme
```
Update README.md with new features, setup instructions, API documentation, and usage examples.
```

#### @api_docs
```
Update API documentation: add endpoint descriptions, request/response examples, error codes, and authentication requirements.
```

#### @architecture_docs
```
Update architecture documentation: system design, component diagrams, data flow, and technical decisions.
```

#### @user_docs
```
Create user documentation: feature guides, tutorials, FAQs, and troubleshooting guides.
```

### Bug Fixes

#### @bug_analysis
```
Perform comprehensive analysis of the bug: root cause, reproduction steps, impact assessment, and fix strategy.
```

#### @bug_fix
```
Fix the bug with proper error handling, logging, and tests to prevent regression.
```

#### @bug_testing
```
Add tests to reproduce the bug and verify the fix. Include edge cases and regression tests.
```

### Feature Development

#### @feature_implementation
```
Implement feature following OpenSpec proposal, design document, and tasks.md. Ensure type safety, error handling, and tests.
```

#### @feature_testing
```
Write comprehensive tests for new feature: unit tests, integration tests, and E2E tests. Target 95%+ coverage.
```

#### @feature_documentation
```
Document new feature: API documentation, user guide, code comments, and architecture notes.
```

### Code Quality & Maintenance

#### @technical_debt
```
Address technical debt: refactor code, improve architecture, update dependencies, and eliminate code smells.
```

#### @dependency_update
```
Update dependencies: review changelogs, test compatibility, update requirements.txt, and verify functionality.
```

#### @code_cleanup
```
Clean up code: remove unused imports, dead code, commented code, and improve code organization.
```

### OpenSpec Integration

#### @openspec_create_proposal
```
Create OpenSpec proposal: proposal.md, tasks.md, optional design.md, and spec deltas. Run validation before submission.
```

#### @openspec_implement
```
Implement OpenSpec change: follow tasks.md checklist, update STATUS.md, and ensure all requirements are met.
```

#### @openspec_archive
```
Archive OpenSpec change after deployment: move to archive/, update specs/, run validation, and update documentation.
```

#### @openspec_sync
```
Synchronize Vibe Kanban task with OpenSpec: update task status based on tasks.md completion, link documents.
```

### Analytics & Reporting

#### @analytics_implementation
```
Implement analytics: metrics collection, data aggregation, visualization, and reporting functionality.
```

#### @reporting
```
Create reporting functionality: data export (PDF, CSV, Excel), custom reports, and scheduled reports.
```

### AI & ML

#### @ai_integration
```
Integrate AI service: configure API, implement error handling, add fallback mechanisms, and optimize prompts.
```

#### @ai_optimization
```
Optimize AI integration: improve prompts, reduce API calls, implement caching, and enhance response quality.
```

### Job Search

#### @job_search_integration
```
Integrate job search platform: implement API client, handle rate limits, parse responses, and store results.
```

#### @job_matching
```
Implement job matching algorithm: skills matching, experience level, location preferences, and ranking.
```

## Tag Categories

### By Priority
- **Critical**: @security_audit, @bug_fix, @database_backup
- **High**: @test_coverage, @performance_optimization, @api_security
- **Medium**: @feature_implementation, @code_refactoring, @api_documentation
- **Low**: @code_cleanup, @update_readme, @dependency_update

### By Phase
- **Planning**: @openspec_review, @openspec_validate, @openspec_design
- **Implementation**: @feature_implementation, @api_endpoint, @component_development
- **Testing**: @add_unit_tests, @test_coverage, @test_e2e
- **Deployment**: @docker_setup, @ci_cd_pipeline, @deployment
- **Maintenance**: @code_refactoring, @technical_debt, @dependency_update

## Usage Examples

### Example 1: Starting a new feature
```
@openspec_review
@openspec_tasks
@feature_implementation
@add_unit_tests
@api_documentation
```

### Example 2: Bug fix
```
@bug_analysis
@bug_fix
@bug_testing
@code_review
```

### Example 3: Performance optimization
```
@performance_optimization
@database_optimization
@caching
@test_performance
```

### Example 4: Security enhancement
```
@security_audit
@security_headers
@input_validation
@test_security
```

## Adding New Tags

When adding new tags:
1. Use descriptive names with @ prefix
2. Include clear instructions
3. Add to appropriate category
4. Update this document
5. Consider priority and phase

