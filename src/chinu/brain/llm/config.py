"""Configuration for LLM providers, loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAIConfig(BaseSettings):
    """Configuration for the OpenAI provider."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_")
    api_key: str
    chat_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"


class GeminiConfig(BaseSettings):
    """Configuration for the Google Gemini provider."""

    model_config = SettingsConfigDict(env_prefix="GEMINI_")
    api_key: str
    chat_model: str = "gemini-1.5-flash"
    embedding_model: str = "text-embedding-004"


class OllamaConfig(BaseSettings):
    """Configuration for the Ollama provider."""

    model_config = SettingsConfigDict(env_prefix="OLLAMA_")
    host: str = "http://localhost:11434"
    chat_model: str = "llama3"
    embedding_model: str = "nomic-embed-text"