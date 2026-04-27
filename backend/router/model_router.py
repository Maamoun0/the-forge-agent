"""
ModelRouter — Routes LLM requests to the appropriate provider (Gemini or Ollama).
Implements fallback chain for reliability.
"""
import asyncio
import logging
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from backend.config import (
    GOOGLE_API_KEY,
    OLLAMA_BASE_URL,
    MODEL_CONFIG,
    FALLBACK_CHAIN,
)
import os

logger = logging.getLogger("forge.router")


class ModelRouter:
    """
    Routes requests to the correct LLM based on agent role.
    Supports automatic fallback if the primary model fails.
    """

    def __init__(self):
        self._model_cache: dict[str, BaseChatModel] = {}

    def _get_model(self, provider: str, model: str, temperature: float = 0.3) -> BaseChatModel:
        """Create or retrieve a cached model instance."""
        cache_key = f"{provider}:{model}:{temperature}"
        if cache_key not in self._model_cache:
            if provider == "gemini":
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not found in environment")
                self._model_cache[cache_key] = ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=api_key,
                    temperature=temperature,
                )
            elif provider == "ollama":
                # Use a subclass to support structured output with json_mode for local Ollama
                class StructuredOllama(ChatOpenAI):
                    def with_structured_output(self, schema, **kwargs):
                        if "method" not in kwargs:
                            kwargs["method"] = "json_mode"
                        return super().with_structured_output(schema, **kwargs)

                self._model_cache[cache_key] = StructuredOllama(
                    model=model,
                    api_key="ollama", # Dummy key for local
                    base_url=f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/v1",
                    temperature=temperature,
                )
            elif provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                self._model_cache[cache_key] = ChatOpenAI(
                    model=model,
                    api_key=api_key,
                    temperature=temperature,
                )
            else:
                raise ValueError(f"Unknown provider: {provider}")
        return self._model_cache[cache_key]

    def get_model_for_role(self, role: str) -> BaseChatModel:
        """Get the configured model for a specific agent role."""
        if role not in MODEL_CONFIG:
            raise ValueError(f"Unknown role: {role}. Available: {list(MODEL_CONFIG.keys())}")

        config = MODEL_CONFIG[role]
        return self._get_model(
            provider=config["provider"],
            model=config["model"],
            temperature=config.get("temperature", 0.3),
        )

    async def invoke_with_fallback(
        self,
        role: str,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = 2,
    ) -> Optional[str]:
        """
        Invoke the model for a role with automatic fallback.
        If the primary model fails, tries the fallback chain.
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        # Try primary model first
        config = MODEL_CONFIG[role]
        try:
            model = self._get_model(config["provider"], config["model"], config.get("temperature", 0.3))
            response = await model.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.warning(f"Primary model failed for role '{role}' ({config['model']}): {e}")

        # Try fallback chain
        for fallback in FALLBACK_CHAIN:
            try:
                logger.info(f"Trying fallback: {fallback['provider']}:{fallback['model']}")
                model = self._get_model(fallback["provider"], fallback["model"])
                response = await model.ainvoke(messages)
                return response.content
            except Exception as e:
                logger.warning(f"Fallback {fallback['model']} failed: {e}")
                continue

        logger.error(f"All models failed for role '{role}'")
        return None

    async def invoke_structured(
        self,
        role: str,
        system_prompt: str,
        user_prompt: str,
        output_schema: type,
    ):
        """
        Invoke the model and parse the output into a Pydantic schema.
        This ensures structured, validated output (anti-hallucination measure).
        """
        model = self.get_model_for_role(role)
        structured_model = model.with_structured_output(output_schema)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        try:
            result = await structured_model.ainvoke(messages)
            return result
        except Exception as e:
            logger.error(f"Structured invoke failed for role '{role}': {e}")
            # Fallback: try raw invoke and manual parse
            raw = await self.invoke_with_fallback(role, system_prompt, user_prompt)
            if raw:
                try:
                    return output_schema.model_validate_json(raw)
                except Exception:
                    logger.error(f"Manual parse also failed for role '{role}'")
            return None


# Singleton instance
router = ModelRouter()
