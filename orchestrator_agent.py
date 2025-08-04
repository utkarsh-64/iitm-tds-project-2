# orchestrator_agent.py
# This is the "manager" or "master" agent. It orchestrates the entire workflow
# by delegating tasks to specialized worker agents.

import os
import json
from openai import OpenAI

# Import the specialized worker agents
from agents import search_scraper_agent
from agents import data_analyzer_agent
from agents import visualization_agent # Re-added the visualization agent

class OrchestratorAgent:
    """The master agent that manages the entire data analysis task."""

    def __init__(self):
        """Initializes the Orchestrator and the OpenAI client."""
        api_key = os.getenv("AIPROXY_TOKEN")
        base_url = "https://aiproxy.sanand.workers.dev/openai/"
        if not api_key or not base_url:
            raise ValueError("API key or base URL not found in environment variables.")
        
        self.llm_client = OpenAI(api_key=api_key, base_url=base_url)
        print("OrchestratorAgent initialized.")

    async def run(self, prompt: str):
        """The main execution method for the entire workflow."""
        
        # Step 1: Create a high-level plan using the LLM. This plan determines
        # which worker agents to call in which order.
        plan = self._generate_plan(prompt)
        print("--- Orchestrator Plan ---")
        print(json.dumps(plan, indent=2))
        print("-------------------------")

        # This will hold the data as it's passed between agents (e.g., the DataFrame)
        shared_context = {}
        results = []

        # Step 2: Execute the plan by calling the worker agents
        for i, task in enumerate(plan.get("tasks", [])):
            agent_name = task.get("agent")
            task_goal = task.get("goal")
            print(f"\nExecuting Task {i+1}: Delegating to '{agent_name}'")
            print(f"  Goal: {task_goal}")

            if agent_name == "SearchAndScrapeAgent":
                # This agent finds and scrapes the data
                data_url = task.get("url") # The plan extracts the URL for the agent
                dataframe = search_scraper_agent.run(url=data_url)
                shared_context["dataframe"] = dataframe # Store data for other agents
            
            elif agent_name == "DataAnalysisAgent":
                # This agent performs SQL-based analysis
                df = shared_context.get("dataframe")
                if df is None:
                    raise ValueError("DataAnalysisAgent cannot run without a dataframe.")
                
                analysis_result = data_analyzer_agent.run(
                    df=df, 
                    question=task_goal, 
                    llm_client=self.llm_client
                )
                results.append(analysis_result)
                print(f"  -> Orchestrator received result: {analysis_result}")

            elif agent_name == "VisualizationAgent":
                # This agent creates plots
                df = shared_context.get("dataframe")
                if df is None:
                    raise ValueError("VisualizationAgent cannot run without a dataframe.")
                
                plot_params = task.get("params", {})
                viz_result = visualization_agent.run(df=df, params=plot_params)
                results.append(viz_result)
                print("  -> Orchestrator received a base64 image.")

        return results


    def _generate_plan(self, prompt: str) -> dict:
        """Uses an LLM to decompose a prompt into a multi-agent plan."""
        print("Orchestrator: Generating multi-agent plan...")
        
        system_prompt = """
You are a master orchestrator agent. Your job is to create a step-by-step plan to fulfill a user's request by delegating tasks to specialized worker agents.

You have access to the following agents:
1.  `SearchAndScrapeAgent`: Finds and retrieves data (like tables) from a given URL.
2.  `DataAnalysisAgent`: Answers a specific question about a data table.
3.  `VisualizationAgent`: Creates a plot or chart from a data table.

Based on the user's prompt, create a JSON plan that outlines the sequence of agent calls.
- For `SearchAndScrapeAgent`, you must extract the URL from the prompt.
- For `DataAnalysisAgent`, formulate a clear, self-contained question for it to answer.
- For `VisualizationAgent`, specify the plot parameters, including type, columns, and styling.

Generate ONLY the JSON plan. Do not add any conversational text.

Example Plan Structure:
{
  "tasks": [
    {
      "agent": "SearchAndScrapeAgent",
      "goal": "Fetch the data table of highest grossing films.",
      "url": "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
    },
    {
      "agent": "DataAnalysisAgent",
      "goal": "How many films grossed more than $2 billion before 2020?"
    },
    {
      "agent": "VisualizationAgent",
      "goal": "Plot Rank vs. Peak with a dotted red regression line.",
      "params": {"plot_type": "scatter", "x_column": "Rank", "y_column": "Peak", "regression_line": true}
    }
  ]
}
"""
        response = self.llm_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        plan_str = response.choices[0].message.content
        return json.loads(plan_str)

