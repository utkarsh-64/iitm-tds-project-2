# main.py
# API server and main entry point for the application.

import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pydantic import BaseModel
import orchestrator_agent # Import the core agent logic

# Load environment variables from a .env file
load_dotenv()

# Define the request body model for JSON requests
class TaskPayload(BaseModel):
    task_text: str

# Initialize the FastAPI application
app = FastAPI(
    title="Data Analysis Agent API",
    description="A multi-agent API that analyzes and visualizes data.",
    version="1.2.0"
)

# Create a single, reusable instance of our agent
data_agent = orchestrator_agent.OrchestratorAgent()

@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple endpoint to check if the server is running."""
    return {"status": "ok", "message": "Data Analysis Agent is running."}

@app.post("/api/", tags=["Core Functionality"])
async def analyze_data(payload: TaskPayload = Body(None), task_file: UploadFile = File(None)):
    """
    The main endpoint that accepts a data analysis task.
    It can accept a JSON payload or a file upload.
    """
    prompt = None
    if payload and payload.task_text:
        prompt = payload.task_text
        print("Received task from JSON payload.")
    elif task_file:
        prompt_bytes = await task_file.read()
        prompt = prompt_bytes.decode('utf-8')
        print(f"Received task from file: {task_file.filename}")

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="No task provided. Please submit a JSON payload with 'task_text' or use 'task_file'."
        )

    try:
        # Execute the task using the agent instance
        print("--- Handing off task to agent ---")
        result = await data_agent.run(prompt=prompt)
        print("--- Agent finished task ---")
        
        # Return the final result
        return JSONResponse(content=result)

    except Exception as e:
        # Log the full error for easier debugging
        print(f"An unexpected error occurred in the main endpoint: {e}")
        # Return a user-friendly error message
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")
