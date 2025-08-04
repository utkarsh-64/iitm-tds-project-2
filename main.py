# main.py
# API server and main entry point for the application.

import os
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pydantic import BaseModel
import orchestrator_agent

# Load environment variables from a .env file
load_dotenv()

# --- Pydantic Model ---
# This defines the expected structure of the incoming JSON request body.
# It's a FastAPI best practice for validation and clarity.
class TaskPayload(BaseModel):
    task_text: str

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Data Analysis Agent API",
    description="A multi-agent API that analyzes and visualizes data.",
    version="1.3.0"
)

# Create a single, reusable instance of our agent
try:
    data_agent = orchestrator_agent.OrchestratorAgent()
except Exception as e:
    # If the agent fails to initialize (e.g., missing API key),
    # we should know immediately.
    print(f"FATAL: Could not initialize OrchestratorAgent: {e}")
    data_agent = None

@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple endpoint to check if the server is running."""
    return {"status": "ok", "message": "Data Analysis Agent is running."}

# --- Main API Endpoint (Simplified and Corrected) ---
@app.post("/api/", tags=["Core Functionality"])
async def analyze_data(payload: TaskPayload):
    """
    Accepts a JSON payload with a 'task_text' field.
    This simplified signature is more robust for API calls.
    """
    if not data_agent:
        raise HTTPException(
            status_code=503,
            detail="Agent is not available due to an initialization error. Check server logs."
        )

    if not payload or not payload.task_text:
        # This check is now more direct.
        raise HTTPException(
            status_code=400,
            detail="Request body must be a JSON object with a 'task_text' key."
        )

    try:
        prompt = payload.task_text
        print(f"Received task: {prompt[:100]}...") # Log first 100 chars

        # Execute the task using the agent instance
        print("--- Handing off task to agent ---")
        result = await data_agent.run(prompt=prompt)
        print("--- Agent finished task ---")
        
        # Return the final result
        return JSONResponse(content=result)

    except Exception as e:
        print(f"An unexpected error occurred while processing the task: {e}")
        # Return a more informative server error
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")
