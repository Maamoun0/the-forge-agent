"""
LangGraph Workflow — The state machine that orchestrates all agents.
This is the "Brain" of The Forge.
"""
import os
import logging
from datetime import datetime
from pathlib import Path

from langgraph.graph import StateGraph, END

from backend.config import WORKSPACE_DIR, MAX_RETRY_LOOPS
from backend.models.state import ProjectState
from backend.agents.ceo import CEOAgent
from backend.agents.analyst import AnalystAgent
from backend.agents.architect import ArchitectAgent
from backend.agents.developer import DeveloperAgent
from backend.agents.integrator import IntegratorAgent
from backend.agents.qa import QAAgent
from backend.agents.reporter import ReporterAgent

logger = logging.getLogger("forge.workflow")

# === Agent Instances ===
ceo = CEOAgent()
analyst = AnalystAgent()
architect = ArchitectAgent()
developer = DeveloperAgent()
integrator = IntegratorAgent()
qa = QAAgent()
reporter = ReporterAgent()


# === Node Functions ===

async def parse_requirements(state: dict) -> dict:
    """CEO parses user input into structured requirements."""
    logger.info("═══ PHASE 1: Parsing Requirements ═══")
    result = await ceo.execute(state)
    return result


async def research(state: dict) -> dict:
    """Analyst enriches requirements with research."""
    logger.info("═══ PHASE 2: Research & Analysis ═══")
    result = await analyst.execute(state)
    return result


async def design_blueprint(state: dict) -> dict:
    """Architect creates the system blueprint."""
    logger.info("═══ PHASE 3: Architecture Design ═══")
    result = await architect.execute(state)
    return result


async def setup_workspace(state: dict) -> dict:
    """Create the project workspace directory."""
    requirements = state.get("requirements", {})
    project_name = requirements.get("name", "project")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace_name = f"{project_name}_{timestamp}"
    workspace_path = str(WORKSPACE_DIR / workspace_name)
    Path(workspace_path).mkdir(parents=True, exist_ok=True)

    logger.info(f"Workspace created: {workspace_path}")
    return {
        "workspace_path": workspace_path,
        "generated_files": {},
        "current_phase": "development",
    }


async def develop(state: dict) -> dict:
    """Developer writes all the code."""
    logger.info("═══ PHASE 4: Development ═══")
    result = await developer.execute(state)
    return result


async def integrate(state: dict) -> dict:
    """Integrator fixes cross-file issues."""
    logger.info("═══ PHASE 5: Integration ═══")
    result = await integrator.execute(state)
    return result


async def quality_check(state: dict) -> dict:
    """QA runs tests and validates code."""
    logger.info("═══ PHASE 6: Quality Assurance ═══")
    result = await qa.execute(state)
    return result


async def fix_errors(state: dict) -> dict:
    """Developer fixes errors found by QA."""
    logger.info("═══ PHASE 6b: Error Fixing ═══")
    errors = state.get("errors", [])
    retry_count = state.get("retry_count", 0) + 1

    if not errors:
        return {"current_phase": "reporting", "retry_count": retry_count}

    # Ask the developer to fix specific errors
    task_list = state.get("task_list", [])
    # Reset failed tasks for retry
    for task in task_list:
        if task["status"] == "failed":
            task["status"] = "pending"

    result = await developer.execute({**state, "task_list": task_list})
    result["retry_count"] = retry_count
    return result


async def generate_report(state: dict) -> dict:
    """Reporter generates documentation."""
    logger.info("═══ PHASE 7: Documentation ═══")
    result = await reporter.execute(state)
    return result


# === Routing Functions ===

def should_fix_or_report(state: dict) -> str:
    """Decide whether to fix errors or proceed to reporting."""
    qa_report = state.get("qa_report", {})
    retry_count = state.get("retry_count", 0)

    if qa_report.get("overall_pass", False):
        return "report"
    elif retry_count >= MAX_RETRY_LOOPS:
        logger.warning(f"Max retries ({MAX_RETRY_LOOPS}) reached. Proceeding with warnings.")
        return "report"
    else:
        return "fix"


def check_error(state: dict) -> str:
    """Check if any phase resulted in an error."""
    if state.get("current_phase") == "error":
        return "end"
    return "continue"


# === Build the Graph ===

def build_workflow() -> StateGraph:
    """Construct the LangGraph state machine."""
    workflow = StateGraph(ProjectState)

    # Add nodes
    workflow.add_node("parse_requirements", parse_requirements)
    workflow.add_node("research", research)
    workflow.add_node("design_blueprint", design_blueprint)
    workflow.add_node("setup_workspace", setup_workspace)
    workflow.add_node("develop", develop)
    workflow.add_node("integrate", integrate)
    workflow.add_node("quality_check", quality_check)
    workflow.add_node("fix_errors", fix_errors)
    workflow.add_node("generate_report", generate_report)

    # Define edges (the flow)
    workflow.set_entry_point("parse_requirements")

    # Parse → Error check
    workflow.add_conditional_edges(
        "parse_requirements",
        check_error,
        {"end": END, "continue": "research"},
    )

    # Research → Architecture
    workflow.add_edge("research", "design_blueprint")

    # Architecture → Error check → Setup workspace
    workflow.add_conditional_edges(
        "design_blueprint",
        check_error,
        {"end": END, "continue": "setup_workspace"},
    )

    # Setup → Develop → Integrate → QA
    workflow.add_edge("setup_workspace", "develop")
    workflow.add_edge("develop", "integrate")
    workflow.add_edge("integrate", "quality_check")

    # QA → Fix or Report (the self-correction loop)
    workflow.add_conditional_edges(
        "quality_check",
        should_fix_or_report,
        {"fix": "fix_errors", "report": "generate_report"},
    )

    # Fix → QA (retry loop)
    workflow.add_edge("fix_errors", "quality_check")

    # Report → END
    workflow.add_edge("generate_report", END)

    return workflow


def create_app(checkpointer=None):
    """Create a compiled, runnable workflow."""
    workflow = build_workflow()
    # Add interrupt to wait for human approval before setup/development
    return workflow.compile(
        interrupt_before=["setup_workspace"],
        checkpointer=checkpointer
    )
