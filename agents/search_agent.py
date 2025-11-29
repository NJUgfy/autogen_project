from agents.base_agent import BaseAgent
from typing import Dict, Any
from tools.brave_search import BraveSearch

class SearchAgent(BaseAgent):
    def __init__(self, name: str = "Searcher", role: str = "Information Retrieval Specialist"):
        super().__init__(name, role)
        self.search_tool = BraveSearch()

    def execute_task(self, task: Dict[str, Any]) -> str:
        query = task.get("query")
        requester = task.get("requester")

        if not query or not requester:
            return "Error: 'query' and 'requester' are required for search tasks."

        print(f"[{self.name}] received search request from '{requester}': {query}")
        
        search_results = self.search_tool.search(query)
        
        print(f"[{self.name}] found results. Sending back to '{requester}'.")
        self.send_message(requester, {
            "type": "search_result",
            "results": search_results
        })
        
        return f"Search completed for: {query}"

    def receive_message(self, sender: str, message: Dict[str, Any]):
        if message.get("type") == "search_request":
            self.execute_task(message)
        else:
            super().receive_message(sender, message)
