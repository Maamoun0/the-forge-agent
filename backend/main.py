"""
The Forge — FastAPI Backend Entry Point.
Handles HTTP & WebSocket connections between the Dashboard and the Agent Engine.
"""
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver

from backend.graph.workflow import create_app
from backend.models.state import ProjectState

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-20s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("forge.main")


# === Lifespan ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔥 The Forge is starting up...")
    yield
    logger.info("🔥 The Forge is shutting down...")


# === App ===
app = FastAPI(
    title="The Forge — AI Agentic Factory",
    description="Multi-agent autonomous software engineering system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Models ===
class ProjectRequest(BaseModel):
    idea: str
    constraints: Optional[str] = None


# === State ===
active_connections: list[WebSocket] = []
current_run: Optional[asyncio.Task] = None
global_memory = None



# === Helpers ===
async def broadcast(message: dict):
    """Send a message to all connected WebSocket clients."""
    data = json.dumps(message)
    disconnected = []
    for ws in active_connections:
        try:
            await ws.send_text(data)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        active_connections.remove(ws)


# === Routes ===

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "online", "service": "The Forge"}


@app.post("/api/projects")
async def start_project(request: ProjectRequest):
    """Start a new project generation (non-WebSocket fallback)."""
    logger.info(f"New project request: {request.idea[:100]}...")

    forge = create_app()
    initial_state = {
        "user_input": request.idea,
        "logs": [],
        "retry_count": 0,
        "human_approved": True,  # Auto-approve for now
        "is_complete": False,
    }

    try:
        result = await forge.ainvoke(initial_state)
        return {
            "status": "complete" if result.get("is_complete") else "error",
            "workspace_path": result.get("workspace_path", ""),
            "final_report": result.get("final_report", ""),
            "files_count": len(result.get("generated_files", {})),
            "logs": result.get("logs", []),
        }
    except Exception as e:
        logger.error(f"Project generation failed: {e}")
        return {"status": "error", "error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time project generation.
    The dashboard connects here to send project ideas and receive live updates.
    """
    global global_memory
    await websocket.accept()
    active_connections.append(websocket)
    logger.info("Dashboard connected via WebSocket")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"DEBUG: Received WebSocket data: {data}")
            message = json.loads(data)

            if message.get("type") == "start_project":
                idea = message.get("idea", "")
                logger.info(f"WebSocket project request: {idea[:100]}...")

                await websocket.send_text(json.dumps({
                    "type": "status",
                    "phase": "starting",
                    "message": "🔥 The Forge is igniting...",
                }))

                if global_memory is None:
                    global_memory = MemorySaver()

                # Setup workflow with memory
                forge = create_app(checkpointer=global_memory)
                config = {"configurable": {"thread_id": "ollama_final_success"}} # Fresh thread ID for final success verification

                
                initial_state = {
                    "user_input": idea,
                    "logs": [],
                    "retry_count": 0,
                    "human_approved": False,
                    "is_complete": False,
                }

                try:
                    # Phase 1: Run until interrupt (approval)
                    logger.info("Starting astream loop...")
                    async for event in forge.astream(initial_state, config=config):
                        logger.info(f"Got event: {list(event.keys())}")
                        for node_name, node_output in event.items():
                            if node_name == "__interrupt__":
                                continue
                            # Send updates to UI
                            await handle_node_output(websocket, node_name, node_output)
                    logger.info("astream loop finished.")

                    # After interrupt, we are in 'approval' phase
                    state = await forge.aget_state(config)
                    if state.next and state.next[0] == "setup_workspace":
                        # In LangGraph 0.1 sometimes values might be a tuple or dict
                        blueprint_data = None
                        if isinstance(state.values, dict):
                            blueprint_data = state.values.get("blueprint")
                        elif isinstance(state.values, tuple) and state.values:
                            blueprint_data = state.values[0].get("blueprint") if isinstance(state.values[0], dict) else None
                        else:
                            try:
                                blueprint_data = state.values.blueprint
                            except AttributeError:
                                pass

                        await websocket.send_text(json.dumps({
                            "type": "blueprint",
                            "blueprint": blueprint_data,
                        }))

                except Exception as e:
                    import traceback
                    error_detail = traceback.format_exc()
                    logger.error(f"Workflow error for idea '{idea[:50]}...':\n{error_detail}")
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": str(e),
                        }))
                    except Exception:
                        logger.warning("Could not send error message to websocket (already closed)")

            elif message.get("type") == "approve_blueprint":
                logger.info("Blueprint approved by user. Resuming...")
                config = {"configurable": {"thread_id": "1"}}

                if global_memory is None:
                    global_memory = MemorySaver()
                forge = create_app(checkpointer=global_memory)


                # Resume workflow
                async for event in forge.astream(None, config=config):
                    for node_name, node_output in event.items():
                        if node_name == "__interrupt__":
                            continue
                        await handle_node_output(websocket, node_name, node_output)

                await websocket.send_text(json.dumps({
                    "type": "complete",
                    "message": "✅ Project generation complete!",
                }))

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("Dashboard disconnected")


async def handle_node_output(websocket, node_name, node_output):
    """Helper to stream node output to websocket."""
    logs = node_output.get("logs", [])
    phase = node_output.get("current_phase", "")
    files = node_output.get("generated_files", {})

    # Send logs
    if logs:
        latest_log = logs[-1] if isinstance(logs, list) and logs else {}
        await websocket.send_text(json.dumps({
            "type": "agent_log",
            "node": node_name,
            "phase": phase,
            "log": latest_log,
        }))

    # Send phase update
    if phase:
        await websocket.send_text(json.dumps({
            "type": "phase_update",
            "phase": phase,
            "node": node_name,
        }))

    # Send files update if any
    if files:
        await websocket.send_text(json.dumps({
            "type": "files_update",
            "files": files,
        }))


# === Entry Point ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
