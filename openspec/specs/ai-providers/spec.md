# ai-providers Specification

## Purpose
TBD - created by archiving change system-audit-and-ai-provider-expansion. Update Purpose after archive.
## Requirements
### Requirement: Multi-Provider Support
The system SHALL support multiple AI providers (Gemini, OpenAI, OpenRouter) and allow switching between them based on configuration.

#### Scenario: Switching providers
- **WHEN** the user selects a preferred provider in settings
- **THEN** all subsequent AI requests (optimization, generation) SHALL use that provider

### Requirement: OpenAI Integration
The system SHALL provide full support for OpenAI models using the standard Chat Completions API.

#### Scenario: Resume optimization with OpenAI
- **WHEN** a resume optimization request is made using OpenAI
- **THEN** the system SHALL return a structured optimization response from GPT-4 (or configured model)

### Requirement: OpenRouter Integration
The system SHALL provide support for OpenRouter models, handling specific headers and model identifiers.

#### Scenario: Skills extraction with OpenRouter
- **WHEN** an extract skills request is made using OpenRouter
- **THEN** the system SHALL correctly communicate with the OpenRouter API and return a list of identified skills

