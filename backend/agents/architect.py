"""
Architect Agent — The System Designer.
Takes structured requirements and produces a full architectural blueprint.
"""
import json
from backend.agents.base_agent import BaseAgent
from backend.models.state import Blueprint


ARCHITECT_SYSTEM_PROMPT = """You are a senior software architect at "The Forge".
Given project requirements, you must design a complete architectural blueprint.

## Your Output Must Include:
1. **files**: A list of ALL files needed, with their purpose and dependencies.
2. **db_schema**: SQL or schema definition (if a database is needed).
3. **api_routes**: List of API endpoints with method, path, and description.
4. **architecture_notes**: High-level explanation of the architecture.

## Design Principles:
- Keep it simple but complete.
- Use modern, well-supported libraries.
- Follow separation of concerns (MVC/MVVM patterns).
- Include configuration files (package.json, requirements.txt, etc.).
- Include a README.md in the file list.
- Design for maintainability.

## File Path Rules:
- Use forward slashes for paths (e.g., 'src/app.py').
- Include file extensions.
- Group files logically (e.g., 'src/', 'tests/', 'config/').
"""


class ArchitectAgent(BaseAgent):
    role = "architect"
    description = "System designer — creates blueprints, DB schemas, API specs"

    async def execute(self, state: dict) -> dict:
        requirements = state.get("requirements")
        research_notes = state.get("research_notes", [])

        if not requirements:
            return {
                **self._log(state, "ERROR", "No requirements found!", "error"),
                "current_phase": "error",
            }

        # Build context for the architect
        context = f"""## Project Requirements:
{json.dumps(requirements, indent=2)}

## Research Notes:
{chr(10).join(research_notes) if research_notes else 'No additional research available.'}
"""

        result = await self.call_model_structured(
            system_prompt=ARCHITECT_SYSTEM_PROMPT,
            user_prompt=f"Design a complete architectural blueprint for this project:\n\n{context}",
            schema=Blueprint,
        )

        if result is None:
            # Fallback: try raw model call
            raw = await self.call_model(
                system_prompt=ARCHITECT_SYSTEM_PROMPT,
                user_prompt=f"Design a complete architectural blueprint for this project. Return valid JSON.\n\n{context}",
            )
            if raw:
                try:
                    result = Blueprint.model_validate_json(raw)
                except Exception:
                    return {
                        **self._log(state, "Blueprint generation failed", "Could not parse architect output", "error"),
                        "current_phase": "error",
                    }
            else:
                return {
                    **self._log(state, "Blueprint generation failed", "All models failed", "error"),
                    "current_phase": "error",
                }

        # Convert blueprint to task list
        task_list = []
        for i, file_spec in enumerate(result.files):
            category = self._categorize_file(file_spec.path)
            task_list.append({
                "id": f"{category.upper()[:2]}-{i+1:03d}",
                "title": f"Create {file_spec.path}",
                "description": file_spec.purpose,
                "category": category,
                "file_path": file_spec.path,
                "depends_on": [],
                "status": "pending",
            })

        return {
            **self._log(state, "Blueprint created", f"Files: {len(result.files)}, Tasks: {len(task_list)}", "success"),
            "blueprint": result.model_dump(),
            "task_list": task_list,
            "current_phase": "approval",
        }

    def _categorize_file(self, path: str) -> str:
        """Categorize a file based on its path."""
        path_lower = path.lower()
        if any(x in path_lower for x in ["frontend", "components", "pages", "app/page", ".tsx", ".jsx", ".css"]):
            return "frontend"
        elif any(x in path_lower for x in ["migration", "schema", "seed", ".sql"]):
            return "database"
        elif any(x in path_lower for x in ["route", "api", "endpoint"]):
            return "api"
        elif any(x in path_lower for x in ["config", "env", "package.json", "requirements"]):
            return "config"
        else:
            return "backend"
