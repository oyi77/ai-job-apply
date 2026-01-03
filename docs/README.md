# Documentation Index

Welcome to the AI Job Application Assistant documentation. This directory contains comprehensive documentation about the project's current state, architecture, APIs, and development practices.

## Documentation Files

### 📊 [00-project-state.md](./00-project-state.md)
**Current project state and status**

- Project overview and status summary
- Completed features checklist
- Architecture overview
- Core capabilities
- API endpoints summary
- Database schema overview
- Services documentation
- Testing status
- Technology stack
- Performance metrics
- Known issues
- Next steps

**Use this when**: You need a quick overview of what's built and what's working.

---

### 🏗️ [01-architecture.md](./01-architecture.md)
**System architecture and design patterns**

- High-level system architecture
- Backend layered architecture
- Frontend component architecture
- Database architecture
- Service architecture
- Security architecture
- Error handling patterns
- Performance optimization strategies
- Deployment architecture
- Testing architecture
- Monitoring and logging

**Use this when**: You need to understand how the system is structured or want to add new features.

---

### 🔌 [02-api-reference.md](./02-api-reference.md)
**Complete API reference documentation**

- Authentication (future)
- Response formats
- All API endpoints with examples:
  - Health & Status
  - Applications (CRUD)
  - Resumes (CRUD)
  - Cover Letters (CRUD)
  - AI Services
  - Job Search
- Request/response examples
- Error codes and handling
- Rate limiting (future)
- Pagination

**Use this when**: You're integrating with the API or need endpoint details.

---

### 🗄️ [03-database-schema.md](./03-database-schema.md)
**Database schema and data models**

- Database configuration
- Schema diagram
- All tables with columns:
  - resumes
  - cover_letters
  - job_applications
  - job_searches
  - ai_activities
  - file_metadata
- Relationships and foreign keys
- Data types and JSON fields
- Indexes and performance
- Migration process
- Backup and recovery

**Use this when**: You need to understand the data model or modify the database schema.

---

### 🛠️ [04-development-guide.md](./04-development-guide.md)
**Development workflow and best practices**

- Getting started guide
- Authentication setup
- Development workflow
- Code style guidelines
- Running tests
- Database management
- Project structure
- Adding new features (step-by-step)
- Debugging guide
- Code quality tools
- Performance optimization
- Common tasks
- Troubleshooting
- Best practices

**Use this when**: You're setting up the development environment or adding new features.

---

### 🔒 [07-security-guide.md](./07-security-guide.md)
**Security best practices and configuration**

- Authentication & Authorization
- Password Security
- Token Management
- Rate Limiting
- CSRF Protection
- Account Lockout
- Input Validation
- File Upload Security
- API Security
- Database Security
- Production Security
- Security Checklist

**Use this when**: You need to understand security features or configure security settings.

---

### 📋 [05-project-proposals.md](./05-project-proposals.md)
**OpenSpec proposals for completing project goals**

- Proposal index and status
- Implementation roadmap
- Priority and effort estimates
- Proposal details and validation
- Next steps and approval process

**Use this when**: You want to understand what needs to be built next or review proposed changes.

---

### 📘 [PRD.md](./PRD.md)
**Product Requirements Document**

- Product vision and mission
- Target audience and personas
- Feature specifications with user stories
- Success criteria and metrics
- User flows and acceptance criteria
- Non-functional requirements
- Timeline and milestones

**Use this when**: You need to understand product requirements, features, or user needs.

---

### 🔧 [TDD.md](./TDD.md)
**Technical Design Document**

- System architecture and design patterns
- Component specifications
- API contracts and data models
- Database design
- Security implementation
- Performance considerations
- Testing strategy
- Deployment architecture
- Technology stack details

**Use this when**: You need detailed technical specifications for implementation.

---

### 🏛️ [HLD.md](./HLD.md)
**High-Level Design Document**

- System architecture overview
- Component interactions
- Data flow diagrams
- Integration architecture
- Deployment architecture
- Scalability design
- Security architecture
- Monitoring and observability

**Use this when**: You need to understand the overall system architecture and design.

---

## Quick Navigation

### By Role

#### **New Developer**
1. Start with [00-project-state.md](./00-project-state.md) for overview
2. Read [04-development-guide.md](./04-development-guide.md) for setup
3. Review [01-architecture.md](./01-architecture.md) for structure

#### **API Consumer**
1. Read [02-api-reference.md](./02-api-reference.md) for endpoints
2. Check [00-project-state.md](./00-project-state.md) for capabilities

#### **Database Administrator**
1. Review [03-database-schema.md](./03-database-schema.md) for schema
2. Check [04-development-guide.md](./04-development-guide.md) for migrations

#### **Architect/Lead Developer**
1. Study [HLD.md](./HLD.md) for high-level architecture
2. Review [TDD.md](./TDD.md) for technical specifications
3. Study [01-architecture.md](./01-architecture.md) for detailed design
4. Review [00-project-state.md](./00-project-state.md) for status
5. Check [04-development-guide.md](./04-development-guide.md) for practices

#### **Product Manager**
1. Read [PRD.md](./PRD.md) for product requirements
2. Review [00-project-state.md](./00-project-state.md) for current status
3. Check [05-project-proposals.md](./05-project-proposals.md) for roadmap

### By Task

#### **Setting Up Development Environment**
→ [04-development-guide.md](./04-development-guide.md) - Getting Started section

#### **Understanding System Architecture**
→ [HLD.md](./HLD.md) - High-level system architecture
→ [TDD.md](./TDD.md) - Technical design and components
→ [01-architecture.md](./01-architecture.md) - Detailed architecture patterns

#### **Integrating with API**
→ [02-api-reference.md](./02-api-reference.md) - Complete API reference

#### **Modifying Database Schema**
→ [03-database-schema.md](./03-database-schema.md) - Schema documentation
→ [04-development-guide.md](./04-development-guide.md) - Database Management section

#### **Adding New Features**
→ [04-development-guide.md](./04-development-guide.md) - Adding New Features section
→ [01-architecture.md](./01-architecture.md) - Architecture patterns

#### **Debugging Issues**
→ [04-development-guide.md](./04-development-guide.md) - Debugging section
→ [04-development-guide.md](./04-development-guide.md) - Troubleshooting section

## Documentation Standards

### Update Frequency
- **Project State**: Updated when major features are completed
- **Architecture**: Updated when architectural changes are made
- **API Reference**: Updated when endpoints are added/modified
- **Database Schema**: Updated when schema changes
- **Development Guide**: Updated when processes change

### Contributing to Documentation
1. Keep documentation up to date with code changes
2. Use clear, concise language
3. Include code examples where helpful
4. Update the index (this file) when adding new docs
5. Follow the existing format and structure

## Related Documentation

### External Resources
- **README.md** (project root): Project overview and quick start
- **backend/README.md**: Backend-specific documentation
- **frontend/README.md**: Frontend-specific documentation
- **openspec/project.md**: Project conventions and tech stack

### Code Documentation
- **API Docs**: Available at `/docs` when running backend (Swagger UI)
- **Type Definitions**: `frontend/src/types/index.ts`
- **Docstrings**: Python code includes comprehensive docstrings

## Status

**Last Updated**: 2025-01-21  
**Documentation Status**: Complete and up to date  
**Coverage**: All major aspects documented  
**New Documents**: PRD, TDD, and HLD added  
**Proposals**: 3 complete proposals ready for review (see [05-project-proposals.md](./05-project-proposals.md))

## New Documentation Added

### Product Requirements Document (PRD)
Comprehensive product documentation including:
- Product vision and mission
- Feature specifications with user stories
- Success criteria and metrics
- User personas and flows
- Non-functional requirements

### Technical Design Document (TDD)
Detailed technical specifications including:
- Component specifications
- API contracts and data models
- Security and performance design
- Testing strategy
- Deployment architecture

### High-Level Design (HLD)
System architecture overview including:
- Component interactions
- Data flow diagrams
- Integration architecture
- Scalability design
- Security architecture

---

**Need help?** Check the relevant documentation file or refer to the development guide's troubleshooting section.

