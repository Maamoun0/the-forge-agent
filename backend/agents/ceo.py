"""
CEO Agent — The Supervisor.
Parses user input into structured requirements and orchestrates the overall flow.
"""
from backend.agents.base_agent import BaseAgent
from backend.models.state import ProjectRequirements


CEO_SYSTEM_PROMPT = """You are the CEO of "The Forge", an AI software engineering company.
Your job is to understand the user's project idea and convert it into clear, structured requirements.

## Rules:
1. Extract ALL features mentioned by the user.
2. Suggest the best tech stack based on the project type.
3. Identify any constraints or special requirements.
4. Be thorough — missing a requirement here means it won't be built.
5. Always output valid structured data.

## Tech Stack Guidelines:
- For web apps: suggest Next.js (frontend) + FastAPI/Express (backend)
- For APIs: suggest FastAPI or Express
- For CLI tools: suggest Python with Click/Typer
- For fullstack: suggest Next.js + FastAPI + PostgreSQL/SQLite
"""


class CEOAgent(BaseAgent):
    role = "ceo"
    description = "Supervisor — parses requirements and orchestrates the project"

    async def execute(self, state: dict) -> dict:
        user_input = state.get("user_input", "")
        if not user_input:
            return {
                **self._log(state, "ERROR", "No user input provided!", "error"),
                "current_phase": "error",
            }

        # Parse user input into structured requirements
        result = await self.call_model_structured(
            system_prompt=CEO_SYSTEM_PROMPT,
            user_prompt=f"Analyze this project idea and extract structured requirements:\n\n{user_input}",
            schema=ProjectRequirements,
        )

        if result is None:
            return {
                **self._log(state, "Failed to parse requirements", "Model returned None", "error"),
                "current_phase": "error",
            }

        return {
            **self._log(state, "Requirements parsed", f"Project: {result.name}, Features: {len(result.features)}", "success"),
            "requirements": result.model_dump(),
            "current_phase": "research",
        }
