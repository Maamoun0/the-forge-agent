"""
Developer Agent — The Lead Coder.
Takes tasks from the blueprint and writes actual code files.
"""
import json
from backend.agents.base_agent import BaseAgent
from backend.tools.file_tool import FileTool


DEVELOPER_SYSTEM_PROMPT = """You are a senior full-stack developer at "The Forge".
You write clean, production-quality code based on the task specification.

## Rules:
1. Write COMPLETE, working code. No placeholders, no "TODO" comments, no "...".
2. Include all necessary imports at the top of the file.
3. Follow the project's tech stack exactly as specified in the blueprint.
4. Use proper error handling.
5. Add brief, helpful comments for complex logic.
6. Return ONLY the code content. No markdown, no code fences, no explanations.

## Quality Standards:
- Functions should be small and focused.
- Use type hints (Python) or TypeScript types (JS/TS).
- Follow naming conventions of the language.
- Include input validation where appropriate.
"""


class DeveloperAgent(BaseAgent):
    role = "developer"
    description = "Lead coder — writes backend/frontend code"

    async def execute(self, state: dict) -> dict:
        task_list = state.get("task_list", [])
        blueprint = state.get("blueprint", {})
        workspace_path = state.get("workspace_path", "")
        generated_files = dict(state.get("generated_files", {}))
        requirements = state.get("requirements", {})

        if not workspace_path:
            return {
                **self._log(state, "ERROR", "No workspace path!", "error"),
                "current_phase": "error",
            }

        file_tool = FileTool(workspace_path)
        updated_logs = dict(state)
        completed = 0
        failed = 0

        for task in task_list:
            if task["status"] != "pending":
                continue

            # Build context with existing files for cross-referencing
            existing_files_summary = "\n".join(
                f"- {path}" for path in generated_files.keys()
            ) or "No files generated yet."

            prompt = f"""## Task: {task['title']}
## Description: {task['description']}
## File to create: {task['file_path']}
## Category: {task['category']}

## Project Requirements:
{json.dumps(requirements, indent=2)}

## Blueprint Architecture:
{blueprint.get('architecture_notes', 'N/A')}

## Existing Files in Project:
{existing_files_summary}

## API Routes (if relevant):
{json.dumps(blueprint.get('api_routes', []), indent=2)}

## DB Schema (if relevant):
{blueprint.get('db_schema', 'N/A')}

Write the COMPLETE code for: {task['file_path']}
Return ONLY the raw code. No markdown fences.
"""

            code = await self.call_model(
                system_prompt=DEVELOPER_SYSTEM_PROMPT,
                user_prompt=prompt,
            )

            if code is None:
                task["status"] = "failed"
                failed += 1
                continue

            # Strip markdown code fences if the model added them
            code = self._strip_code_fences(code)

            # Write to workspace (syntax guard will validate)
            result = file_tool.write_file(task["file_path"], code)

            if result["status"] == "success":
                task["status"] = "done"
                generated_files[task["file_path"]] = code
                completed += 1
            elif result["status"] == "rejected":
                # Syntax error — try to self-correct once
                fix_prompt = f"""The following code has a syntax error:
Error: {result['error']}

Original code:
{code}

Fix the syntax error and return the corrected code. Return ONLY the raw code.
"""
                fixed_code = await self.call_model(
                    system_prompt="You are a code fixer. Fix the syntax error. Return ONLY the corrected code.",
                    user_prompt=fix_prompt,
                )
                if fixed_code:
                    fixed_code = self._strip_code_fences(fixed_code)
                    retry_result = file_tool.write_file(task["file_path"], fixed_code)
                    if retry_result["status"] == "success":
                        task["status"] = "done"
                        generated_files[task["file_path"]] = fixed_code
                        completed += 1
                    else:
                        task["status"] = "failed"
                        failed += 1
                else:
                    task["status"] = "failed"
                    failed += 1
            else:
                task["status"] = "failed"
                failed += 1

        return {
            **self._log(state, "Development complete", f"Completed: {completed}, Failed: {failed}", "success" if failed == 0 else "warning"),
            "task_list": task_list,
            "generated_files": generated_files,
            "current_phase": "integration",
        }

    def _strip_code_fences(self, code: str) -> str:
        """Remove markdown code fences that LLMs sometimes add."""
        code = code.strip()
        if code.startswith("```"):
            # Remove first line (```python or ```)
            lines = code.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)
        return code
