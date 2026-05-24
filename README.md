# llm-inference-gateway
A self-hosted LLM inference gateway built with FastAPI, Redis, and pgvector. Handles API key auth, token bucket rate limiting, semantic caching, automatic provider fallback (Anthropic ↔ OpenAI), circuit breaking, cost tracking, and a live admin dashboard. Drop-in OpenAI-compatible API.
