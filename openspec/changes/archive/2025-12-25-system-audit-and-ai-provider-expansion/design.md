# Design: System Audit and AI Provider Expansion

## Context
The application currently uses `AIProviderManager` to handle multiple AI backends. It has placeholder/partial support for OpenAI and LocalAI, but lacks OpenRouter. Achieving "0 error" requires a unified verification strategy.

## Goals
- Unified AI Provider interface implementation for Gemini, OpenAI, and OpenRouter.
- 100% test coverage for critical business logic paths.
- Seamless provider switching via Settings UI.

## Architecture Decisions

### 1. OpenRouter Provider Implementation
Implement `OpenRouterProvider` inheriting from `AIProvider`. It will use the OpenAI-compatible API format but with specific OpenRouter headers (`HTTP-Referer`, `X-Title`).

```python
class OpenRouterProvider(AIProvider):
    async def generate_text(self, prompt: str, **kwargs) -> AIResponse:
        # Implementation using OpenRouter API
```

### 2. Configuration Schema Update
Update `backend/src/config.py` to support OpenRouter settings.

```python
openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
openrouter_model: str = Field(default="meta-llama/llama-3-8b-instruct", env="OPENROUTER_MODEL")
```

### 3. Verification Strategy
- **Backend**: Use `pytest` with `pytest-asyncio`. Mock all external AI API calls.
- **Frontend**: Use `Vitest` and `React Testing Library`.
- **E2E**: Manual verification of flows after automated tests pass.

## Risks & Trade-offs
- **API Latency**: Different providers have varying response times. Implementation must handle timeouts gracefully.
- **Consistency**: Model outputs differ in formatting. Prompt engineering must be adjusted to ensure consistent JSON structures when required.
