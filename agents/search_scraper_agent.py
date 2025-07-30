# agents/search_scraper_agent.py
# This worker agent is specialized in finding and scraping data from the web.

import pandas as pd
import requests

def run(url: str) -> pd.DataFrame:
    """
    Entry point for the SearchAndScrapeAgent.
    
    In a more advanced version, this agent could use a search tool to find the URL.
    For now, it accepts a URL directly from the orchestrator.
    """
    print("SearchAndScrapeAgent: Running...")
    
    if not url:
        raise ValueError("SearchAndScrapeAgent requires a URL to run.")
        
    try:
        # Use a common user-agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        tables = pd.read_html(response.text)
        if not tables:
            raise ValueError(f"No HTML tables found at the URL: {url}")

        main_table = max(tables, key=lambda df: df.size)
        print(f"SearchAndScrapeAgent: Success. Returning table with shape {main_table.shape}.")
        return main_table

    except requests.exceptions.RequestException as e:
        print(f"SearchAndScrapeAgent Error: Network request failed. {e}")
        raise
    except Exception as e:
        print(f"SearchAndScrapeAgent Error: An unexpected error occurred. {e}")
        raise
