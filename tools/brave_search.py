import os
import requests
from dotenv import load_dotenv

class BraveSearch:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY not found in .env file")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    def search(self, query: str, num_results: int = 5):
        if not self.api_key or self.api_key == "your_brave_api_key_here":
            return "Error: Brave Search API key not configured."
            
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        params = {
            "q": query,
            "count": num_results,
        }
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            results = response.json()
            
            snippets = []
            if "web" in results and "results" in results["web"]:
                for result in results["web"]["results"]:
                    snippets.append(f"Title: {result.get('title', 'N/A')}\n"
                                    f"URL: {result.get('url', 'N/A')}\n"
                                    f"Snippet: {result.get('description', 'N/A')}\n---")
            
            return "\n".join(snippets) if snippets else "No results found."

        except requests.exceptions.RequestException as e:
            return f"Error calling Brave Search API: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
