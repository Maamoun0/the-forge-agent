"""
Analyst Agent — The Researcher.
Enriches project requirements by gathering additional information.
"""
from backend.agents.base_agent import BaseAgent


ANALYST_SYSTEM_PROMPT = """You are a research analyst at "The Forge".
Your job is to enrich project requirements with technical insights.

## Your Tasks:
1. Identify any ambiguities in the requirements.
2. Suggest best practices for the chosen tech stack.
3. Recommend specific libraries or tools.
4. Note any potential challenges or gotchas.
5. Provide specific version recommendations.

## Output Format:
Return a numbered list of research findings and recommendations.
Be specific and actionable. Each finding should help the developer write better code.
"""


class AnalystAgent(BaseAgent):
    role = "analyst"
    description = "Researcher — enriches requirements with technical insights"

    async def execute(self, state: dict) -> dict:
        requirements = state.get("requirements", {})

        if not requirements:
            return {
                **self._log(state, "Skip", "No requirements to research", "info"),
                "current_phase": "architecture",
                "research_notes": [],
            }

        prompt = f"""Analyze these project requirements and provide research insights:

## Requirements:
- Name: {requirements.get('name', 'Unknown')}
- Type: {requirements.get('project_type', 'Unknown')}
- Description: {requirements.get('description', '')}
- Features: {', '.join(str(f) for f in requirements.get('features', []))}
- Tech Stack: {requirements.get('tech_stack', {})}
- Constraints: {', '.join(str(c) for c in requirements.get('constraints', []))}

Provide actionable technical insights, library recommendations, and potential challenges.
"""

        response = await self.call_model(
            system_prompt=ANALYST_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        research_notes = []
        if response:
            research_notes = [response]

        return {
            **self._log(state, "Research complete", f"Notes: {len(research_notes)}", "success"),
            "research_notes": research_notes,
            "current_phase": "architecture",
        }
