"""
BaseAgent — Abstract base class for all Forge agents.
Every agent inherits from this and implements `execute()`.
"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from backend.models.state import ProjectState, AgentLog
from backend.router.model_router import router


logger = logging.getLogger("forge.agent")


class BaseAgent(ABC):
    """
    Base class for all agents in The Forge.
    Provides common utilities: logging, model access, state manipulation.
    """

    role: str = "base"
    description: str = "Base agent"

    def __init__(self):
        self.logger = logging.getLogger(f"forge.agent.{self.role}")

    def _log(self, state: dict, action: str, detail: str = "", status: str = "info") -> dict:
        """Add a log entry to the shared state."""
        log_entry = AgentLog(
            agent=self.role,
            action=action,
            detail=detail,
            status=status,
            timestamp=datetime.now().isoformat(),
        )
        logs = list(state.get("logs", []))
        logs.append(log_entry.model_dump())
        return {"logs": logs}

    async def call_model(self, system_prompt: str, user_prompt: str) -> str | None:
        """Call the LLM assigned to this agent's role with fallback support."""
        self.logger.info(f"[{self.role.upper()}] Calling model...")
        result = await router.invoke_with_fallback(
            role=self.role,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        if result is None:
            self.logger.error(f"[{self.role.upper()}] All models failed!")
        return result

    async def call_model_structured(self, system_prompt: str, user_prompt: str, schema: type):
        """Call the LLM and enforce structured output via Pydantic schema."""
        self.logger.info(f"[{self.role.upper()}] Calling model (structured output)...")
        return await router.invoke_structured(
            role=self.role,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=schema,
        )

    @abstractmethod
    async def execute(self, state: dict) -> dict:
        """
        Execute the agent's task.
        Receives the current ProjectState, returns a partial state update.
        """
        ...

    def __repr__(self):
        return f"<Agent:{self.role}>"
