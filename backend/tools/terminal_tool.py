"""
Terminal Tool — Safe command execution with timeout and output capture.
"""
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger("forge.tools.terminal")

# Commands that are NEVER allowed (security)
BLOCKED_COMMANDS = [
    "rm -rf /", "del /s /q C:", "format",
    "shutdown", "reboot", "mkfs",
    ":(){ :|:& };:",  # fork bomb
]


class TerminalTool:
    """
    Executes shell commands within the project workspace.
    Includes timeout protection and output capture.
    """

    def __init__(self, workspace_path: str, timeout: int = 60):
        self.workspace = Path(workspace_path).resolve()
        self.timeout = timeout

    def _is_safe(self, command: str) -> tuple[bool, str]:
        """Basic safety check for dangerous commands."""
        cmd_lower = command.lower().strip()
        for blocked in BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                return False, f"Blocked dangerous command: {blocked}"
        return True, ""

    async def run(self, command: str, timeout: Optional[int] = None) -> dict:
        """
        Execute a command in the workspace directory.
        Returns structured output with stdout, stderr, and return code.
        """
        is_safe, reason = self._is_safe(command)
        if not is_safe:
            logger.error(f"BLOCKED: {command} — {reason}")
            return {
                "status": "blocked",
                "command": command,
                "error": reason,
                "stdout": "",
                "stderr": "",
                "return_code": -1,
            }

        effective_timeout = timeout or self.timeout
        logger.info(f"Executing: {command} (timeout: {effective_timeout}s)")

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=str(self.workspace),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=effective_timeout,
            )

            result = {
                "status": "success" if process.returncode == 0 else "error",
                "command": command,
                "stdout": stdout.decode("utf-8", errors="replace")[-5000:],  # Last 5000 chars
                "stderr": stderr.decode("utf-8", errors="replace")[-2000:],  # Last 2000 chars
                "return_code": process.returncode,
            }

            if process.returncode != 0:
                logger.warning(f"Command failed (rc={process.returncode}): {command}")
            else:
                logger.info(f"Command succeeded: {command}")

            return result

        except asyncio.TimeoutError:
            logger.error(f"Command timed out after {effective_timeout}s: {command}")
            try:
                process.kill()
            except Exception:
                pass
            return {
                "status": "timeout",
                "command": command,
                "stdout": "",
                "stderr": f"Command timed out after {effective_timeout} seconds",
                "return_code": -1,
            }
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                "status": "error",
                "command": command,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
            }

    async def run_and_check(self, command: str) -> tuple[bool, str]:
        """Run a command and return (success: bool, output: str)."""
        result = await self.run(command)
        success = result["return_code"] == 0
        output = result["stdout"] if success else result["stderr"]
        return success, output
