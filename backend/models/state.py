"""
ProjectState — The shared memory object that flows through the LangGraph state machine.
Every agent reads from and writes to this state.
"""
from typing import TypedDict, Optional
from pydantic import BaseModel, Field, AliasChoices


# === Structured Sub-Models (Pydantic) ===

class ProjectRequirements(BaseModel):
    """Structured representation of a project's requirements."""
    name: str = Field(
        default="project-forge",
        description="Project name (slug format, e.g. 'task-manager')", 
        validation_alias=AliasChoices("name", "project_name", "title")
    )
    description: str = Field(
        default="No description provided.",
        description="Full project description", 
        validation_alias=AliasChoices("description", "project_description", "development_notes", "notes", "summary")
    )
    project_type: str = Field(
        default="other",
        description="Type: 'web-app', 'api', 'cli', 'fullstack', 'other'",
        validation_alias=AliasChoices("project_type", "type")
    )
    features: list = Field(default_factory=list, description="List of required features")
    tech_stack: dict = Field(default_factory=dict, description="Suggested tech stack")
    constraints: list = Field(default_factory=list, description="Constraints or special requirements")
    target_audience: str = Field(default="personal", description="Who is this for?")

    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }


class BlueprintFile(BaseModel):
    """A single file in the project blueprint."""
    path: str = Field(description="Relative file path, e.g. 'src/app.py'")
    purpose: str = Field(description="What this file does")
    dependencies: Optional[list[str]] = Field(default_factory=list, description="Other files this depends on")


class Blueprint(BaseModel):
    """Full architectural blueprint for the project."""
    files: list[BlueprintFile] = Field(default_factory=list)
    db_schema: Optional[str] = Field(default=None, description="SQL or schema definition")
    api_routes: Optional[list[dict]] = Field(default_factory=list, description="List of API endpoints")
    architecture_notes: str = Field(default="", description="High-level architecture explanation")

    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }


class TaskItem(BaseModel):
    """A single development task."""
    id: str = Field(description="Unique task ID, e.g. 'BE-001'")
    title: str = Field(description="Short task title")
    description: str = Field(description="Detailed instructions for the agent")
    category: str = Field(description="Category: 'backend', 'frontend', 'database', 'api', 'config'")
    file_path: str = Field(description="Target file to create/modify")
    depends_on: list[str] = Field(default_factory=list, description="Task IDs this depends on")
    status: str = Field(default="pending", description="pending, in_progress, done, failed")


class AgentLog(BaseModel):
    """A single log entry from an agent."""
    agent: str = Field(description="Agent role name")
    action: str = Field(description="What the agent did")
    detail: str = Field(default="", description="Additional details")
    status: str = Field(default="info", description="info, success, warning, error")
    timestamp: str = Field(default="")


class QAReport(BaseModel):
    """Report from the QA agent."""
    tests_run: int = Field(default=0)
    tests_passed: int = Field(default=0)
    tests_failed: int = Field(default=0)
    lint_errors: list[str] = Field(default_factory=list)
    runtime_errors: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    overall_pass: bool = Field(default=False)


# === The Master State ===

class ProjectState(TypedDict, total=False):
    """
    The central state object that flows through the entire LangGraph pipeline.
    Every agent reads from and writes to specific keys in this state.
    """
    # --- Input ---
    user_input: str                          # Raw user input (project idea)

    # --- Phase 1: Requirements ---
    requirements: Optional[dict]             # Parsed ProjectRequirements
    research_notes: list[str]                # Analyst's research findings

    # --- Phase 2: Architecture ---
    blueprint: Optional[dict]                # The architectural blueprint
    task_list: list[dict]                    # List of TaskItems

    # --- Phase 3: Development ---
    generated_files: dict[str, str]          # {file_path: file_content}
    workspace_path: str                      # Absolute path to project workspace

    # --- Phase 4: Quality Assurance ---
    qa_report: Optional[dict]                # QA results
    errors: list[str]                        # Current errors to fix
    retry_count: int                         # Number of fix-retry cycles

    # --- Phase 5: Output ---
    final_report: str                        # Generated documentation
    project_zip_path: str                    # Path to zipped project

    # --- Meta ---
    logs: list[dict]                         # All agent logs (for dashboard)
    current_phase: str                       # Current execution phase
    human_approved: bool                     # Whether blueprint was approved
    is_complete: bool                        # Whether the project is done
