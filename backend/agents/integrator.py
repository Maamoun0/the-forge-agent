"""
Integrator Agent — Merges all generated files and fixes cross-file issues.
"""
import json
from backend.agents.base_agent import BaseAgent
from backend.tools.file_tool import FileTool


INTEGRATOR_SYSTEM_PROMPT = """You are a code integrator at "The Forge".
Your job is to review all generated files and fix cross-file issues.

## What to Fix:
1. Broken import statements (wrong paths, missing modules).
2. Inconsistent naming (a function called 'getUser' in one file but 'get_user' in another).
3. Missing exports or module declarations.
4. Environment variable references that don't match .env files.

## Rules:
- Only fix integration issues. Do NOT rewrite business logic.
- Return a JSON array of fixes, each with: {"file": "path", "old": "old_content", "new": "new_content"}
- If no fixes needed, return an empty array: []
"""


class IntegratorAgent(BaseAgent):
    role = "integrator"
    description = "Integrator — fixes imports, paths, merges files"

    async def execute(self, state: dict) -> dict:
        workspace_path = state.get("workspace_path", "")
        generated_files = state.get("generated_files", {})

        if not workspace_path or not generated_files:
            return {
                **self._log(state, "Skip", "No files to integrate", "info"),
                "current_phase": "qa",
            }

        file_tool = FileTool(workspace_path)

        # Build a summary of all files for the integrator
        files_summary = ""
        for path, content in generated_files.items():
            truncated = content[:3000] if len(content) > 3000 else content
            files_summary += f"\n\n=== {path} ===\n{truncated}"

        prompt = f"""Review these project files and identify cross-file integration issues.

## Files:
{files_summary}

Return a JSON array of fixes needed. Each fix should have:
- "file": the file path to modify
- "old": the exact text to replace
- "new": the replacement text

If no fixes are needed, return: []
"""

        response = await self.call_model(
            system_prompt=INTEGRATOR_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        fixes_applied = 0
        if response:
            try:
                # Extract JSON from response
                response = response.strip()
                if response.startswith("```"):
                    lines = response.split("\n")[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    response = "\n".join(lines)

                fixes = json.loads(response)
                if isinstance(fixes, list):
                    for fix in fixes:
                        if all(k in fix for k in ["file", "old", "new"]):
                            result = file_tool.edit_file(fix["file"], fix["old"], fix["new"])
                            if result["status"] == "success":
                                fixes_applied += 1
                                # Update in-memory copy
                                if fix["file"] in generated_files:
                                    generated_files[fix["file"]] = generated_files[fix["file"]].replace(
                                        fix["old"], fix["new"], 1
                                    )
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Could not parse integrator response: {e}")

        return {
            **self._log(state, "Integration complete", f"Fixes applied: {fixes_applied}", "success"),
            "generated_files": generated_files,
            "current_phase": "qa",
        }
