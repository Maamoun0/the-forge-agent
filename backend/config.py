"""
Forge Configuration — Central configuration for all models, paths, and limits.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BASE_DIR.parent / "workspaces"
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

# === Google AI Studio (Gemini) ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# === Ollama (Local Models) ===
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# === Safety Limits ===
MAX_RETRY_LOOPS = int(os.getenv("MAX_RETRY_LOOPS", "5"))
MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "50"))

# === Model Assignments ===
# Each agent role is mapped to a specific model.
# Cloud models use Gemini via Google AI Studio.
# Local models use Ollama's OpenAI-compatible API.
MODEL_CONFIG = {
    "ceo": {
        "provider": "ollama",
        "model": "qwen3-coder:30b",
        "temperature": 0.3,
        "description": "Supervisor — strategic decisions, orchestration, final approval",
    },
    "analyst": {
        "provider": "ollama",
        "model": "qwen3-coder:30b",
        "temperature": 0.4,
        "description": "Researcher — web search, requirement enrichment",
    },
    "architect": {
        "provider": "ollama",
        "model": "qwen3-coder:30b",
        "temperature": 0.2,
        "description": "System designer — blueprints, DB schema, API specs",
    },
    "developer": {
        "provider": "ollama",
        "model": "qwen3-coder:30b",
        "temperature": 0.3,
        "description": "Lead coder — writes backend/frontend code",
    },
    "qa": {
        "provider": "ollama",
        "model": "qwen3-coder:30b",
        "temperature": 0.1,
        "description": "QA engineer — writes tests, runs them, reports errors",
    },
    "integrator": {
        "provider": "ollama",
        "model": "qwen3-coder:30b",
        "temperature": 0.1,
        "description": "Integrator — fixes imports, paths, merges files",
    },
    "reporter": {
        "provider": "ollama",
        "model": "qwen3-coder:30b",
        "temperature": 0.5,
        "description": "Reporter — generates documentation and project reports",
    },
}

# === Fallback Chain ===
# If primary model fails, try these in order
FALLBACK_CHAIN = [
    {"provider": "ollama", "model": "qwen3-coder:30b"},
]
