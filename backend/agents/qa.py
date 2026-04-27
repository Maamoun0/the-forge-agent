"""
QA Agent — The Quality Assurance Engineer.
Runs tests, linting, and validates the generated codebase.
"""
import json
from backend.agents.base_agent import BaseAgent
from backend.tools.terminal_tool import TerminalTool
from backend.tools.file_tool import FileTool
from backend.models.state import QAReport


QA_SYSTEM_PROMPT = """You are a QA Engineer at "The Forge".
Your job is to review the generated code, identify issues, and report them.

## What to Check:
1. Missing imports or broken references between files.
2. Undefined variables or functions.
3. Missing error handling.
4. Security issues (hardcoded secrets, SQL injection, etc.).
5. Logic errors in the business logic.

## Output Format:
Report your findings as a structured QA report.
"""


class QAAgent(BaseAgent):
    role = "qa"
    description = "QA Engineer — tests code and reports errors"

    async def execute(self, state: dict) -> dict:
        workspace_path = state.get("workspace_path", "")
        generated_files = state.get("generated_files", {})
        requirements = state.get("requirements", {})

        if not workspace_path:
            return {
                **self._log(state, "ERROR", "No workspace path!", "error"),
                "current_phase": "error",
            }

        terminal = TerminalTool(workspace_path)
        file_tool = FileTool(workspace_path)

        lint_errors = []
        runtime_errors = []
        suggestions = []

        # Step 1: Check for Python files and run syntax check
        py_files = [f for f in generated_files.keys() if f.endswith(".py")]
        for py_file in py_files:
            success, output = await terminal.run_and_check(f"python -m py_compile {py_file}")
            if not success:
                lint_errors.append(f"Syntax error in {py_file}: {output}")

        # Step 2: Check for package.json and run npm checks
        if file_tool.file_exists("package.json"):
            success, output = await terminal.run_and_check("npm install --dry-run 2>&1")
            if not success:
                runtime_errors.append(f"NPM dependency issues: {output[:500]}")

        # Step 3: LLM-powered code review
        files_summary = ""
        for path, content in generated_files.items():
            # Limit content to prevent context overflow
            truncated = content[:2000] if len(content) > 2000 else content
            files_summary += f"\n\n--- {path} ---\n{truncated}"

        review_prompt = f"""Review these generated files for issues:

## Project Requirements:
{json.dumps(requirements, indent=2)}

## Generated Files:
{files_summary}

List any issues found. Focus on:
1. Missing imports between files
2. Broken function calls
3. Missing error handling
4. Any hardcoded values that should be configurable
"""

        review = await self.call_model(
            system_prompt=QA_SYSTEM_PROMPT,
            user_prompt=review_prompt,
        )

        if review:
            # Parse review for actionable items
            review_lower = review.lower()
            if any(word in review_lower for word in ["error", "bug", "issue", "missing", "broken", "undefined"]):
                suggestions.append(review)

        # Build QA Report
        total_checks = len(py_files) + 1  # +1 for LLM review
        passed = total_checks - len(lint_errors) - len(runtime_errors)
        overall_pass = len(lint_errors) == 0 and len(runtime_errors) == 0

        qa_report = QAReport(
            tests_run=total_checks,
            tests_passed=max(0, passed),
            tests_failed=len(lint_errors) + len(runtime_errors),
            lint_errors=lint_errors,
            runtime_errors=runtime_errors,
            suggestions=suggestions,
            overall_pass=overall_pass,
        )

        errors = lint_errors + runtime_errors

        next_phase = "reporting" if overall_pass else "fixing"

        return {
            **self._log(
                state,
                "QA Complete",
                f"Pass: {qa_report.tests_passed}/{qa_report.tests_run}, Errors: {len(errors)}",
                "success" if overall_pass else "warning",
            ),
            "qa_report": qa_report.model_dump(),
            "errors": errors,
            "current_phase": next_phase,
        }
