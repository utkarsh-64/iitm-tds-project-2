# agents/visualization_agent.py
# This worker agent is specialized in creating data visualizations.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def run(df: pd.DataFrame, params: dict) -> str:
    """
    Entry point for the VisualizationAgent.
    It generates a plot based on the provided parameters.
    """
    print("VisualizationAgent: Running...")

    plot_type = params.get("plot_type", "scatter")
    x_col = params.get("x_column")
    y_col = params.get("y_column")

    if not x_col or not y_col:
        raise ValueError("VisualizationAgent requires X and Y columns.")

    plt.figure(figsize=(8, 6))
    
    # This agent could be expanded to handle many plot types
    if plot_type == "scatter":
        sns.scatterplot(data=df, x=x_col, y=y_col)
        if params.get("regression_line"):
            # Ensure the regression line is red and dotted as per potential requirements
            sns.regplot(data=df, x=x_col, y=y_col, scatter=False, color='red', line_kws={'linestyle':'--'})
    else:
        # Placeholder for other plot types like bar, line, etc.
        raise ValueError(f"Plot type '{plot_type}' is not yet supported.")

    plt.title(f'Plot of {y_col} vs. {x_col}')
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid(True)
    
    # Save plot to an in-memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    print("VisualizationAgent: Success. Returning base64 encoded image.")
    return f"data:image/png;base64,{image_base64}"
