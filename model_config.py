"""Shared model configuration for OpenAI-compatible providers."""

import os

from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "nebius").lower()
NEBIUS_BASE_URL = os.getenv(
    "NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"
)
NEBIUS_MODEL = os.getenv(
    "NEBIUS_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct"
)
NEBIUS_EMBEDDING_MODEL = os.getenv(
    "NEBIUS_EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-8B"
)


def chat_model_kwargs() -> dict:
    """Return LangChain ChatOpenAI settings for the selected provider."""
    if AI_PROVIDER == "nebius":
        return {
            "model": NEBIUS_MODEL,
            "api_key": os.getenv("NEBIUS_API_KEY"),
            "base_url": NEBIUS_BASE_URL,
            "disable_streaming": "tool_calling",
        }

    return {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "api_key": os.getenv("OPENAI_API_KEY"),
    }


def embedding_model_kwargs() -> dict:
    """Return LangChain OpenAIEmbeddings settings for the selected provider."""
    if os.getenv("EMBEDDING_PROVIDER", "openai").lower() == "nebius":
        return {
            "model": NEBIUS_EMBEDDING_MODEL,
            "api_key": os.getenv("NEBIUS_API_KEY"),
            "base_url": NEBIUS_BASE_URL,
            "tiktoken_enabled": False,
        }

    return {
        "model": "text-embedding-3-small",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
