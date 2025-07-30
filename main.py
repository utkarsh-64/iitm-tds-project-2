# main.py
# API server and main entry point for the application.

import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import orchestrator_agent# Import the core agent logic

# Load environment variables from a .env file
load_dotenv()

# Initialize the FastAPI application
app = FastAPI(
    title="Data Analysis Agent API",
    description="A simplified API that uses an LLM to analyze and visualize data.",
    version="1.1.0"
)

# Create a single, reusable instance of our agent
data_agent = orchestrator_agent.OrchestratorAgent()

@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple endpoint to check if the server is running."""
    return {"status": "ok", "message": "Data Analysis Agent is running."}

@app.post("/api/", tags=["Core Functionality"])
async def analyze_data(task_file: UploadFile = File(None), task_text: str = Form(None)):
    """
    The main endpoint that accepts a data analysis task.

    Submit a task via file upload or a text field.
    - curl with file: `curl -X POST http://127.0.0.1:8000/api/ -F "task_file=@question.txt"`
    - curl with text: `curl -X POST http://127.0.0.1:8000/api/ -F "task_text=Your question"`
    """
    if not task_file and not task_text:
        raise HTTPException(
            status_code=400,
            detail="No task provided. Please submit via 'task_file' or 'task_text'."
        )

    try:
        # Determine the source of the prompt
        if task_file:
            prompt_bytes = await task_file.read()
            prompt = prompt_bytes.decode('utf-8')
            print(f"Received task from file: {task_file.filename}")
        else:
            prompt = task_text
            print("Received task from text form.")

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

# To run this server:
# 1. Make sure you have a .env file with your API keys.
# 2. Run `uvicorn main:app --reload` in your terminal.
