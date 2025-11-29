from agents.base_agent import BaseAgent
from typing import Dict, Any
from llm.openai_llm import OpenAILLM
from tools.file_tools import read_file, write_to_file
from tools.brave_search import BraveSearch
import os

class CoderAgent(BaseAgent):
    def __init__(self, name: str = "Coder", role: str = "Code Generation Specialist"):
        super().__init__(name, role)
        self.llm = OpenAILLM()
        self.search_tool = BraveSearch()

    def _strip_markdown(self, code: str) -> str:
        lines = code.strip().split('\n')
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
            
        return "\n".join(lines).strip()

    def execute_task(self, task: Dict[str, Any]) -> str:
        print(f"[{self.name}] received task: {task.get('description')}")
        if task.get("type") == "coding_task":
            return self._handle_coding_task(task)
        elif task.get("type") == "evaluation_result" and task.get("status") == "requires_revision":
            return self._handle_revision_request(task)
        
        return "No action taken."

    def _handle_coding_task(self, task: Dict[str, Any]) -> str:
        file_path = task.get("file_path")
        description = task.get("description")
        if not file_path or not description:
            return "Error: 'file_path' and 'description' are required for coding tasks."

        print(f"[{self.name}] starting to code for: {description}")
        
        current_code = ""
        if os.path.exists(file_path):
            current_code = read_file(file_path)

        generated_code = self._generate_code(description, current_code)
        cleaned_code = self._strip_markdown(generated_code)
        
        write_to_file(file_path, cleaned_code)
        
        print(f"[{self.name}] finished coding. Notifying Planner.")
        self.send_message("Planner", {"type": "task_complete"})
        
        return f"Code generated for {file_path}."

    def _handle_revision_request(self, task: Dict[str, Any]) -> str:
        file_path = task.get("file_path")
        feedback = task.get("feedback")

        if not file_path or not feedback:
            return "Error: 'file_path' and 'feedback' are required for revision requests."

        print(f"[{self.name}] received revision request: {feedback}")

        current_code = read_file(file_path)
        
        revised_code = self._revise_code(feedback, current_code)
        cleaned_code = self._strip_markdown(revised_code)
        write_to_file(file_path, cleaned_code)

        print(f"[{self.name}] finished revision. Notifying Planner.")
        self.send_message("Planner", {"type": "task_complete"})

        return f"Code revised for {file_path}."

    def _generate_code(self, description: str, current_code: str = "") -> str:
        search_results = self.search_tool.search(description)
        
        system_prompt = f"""
You are an expert programmer. Your task is to write clean, efficient, and correct code based on a given description.
You will be given a description of the task, the current content of the file, and some search results for context.
Your output MUST be ONLY the complete, updated code for the file. Do NOT include any explanations, markdown, or any text other than the code itself.

**Search Results:**
{search_results}
"""
        user_message = f"**Task Description:**\n{description}\n\n**Current Code:**\n```\n{current_code}\n```\n\nPlease provide the complete, updated code for the file."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self.llm.generate_completion(messages, temperature=0.1)

    def _revise_code(self, feedback: str, current_code: str) -> str:
        search_results = self.search_tool.search(feedback)

        system_prompt = f"""
You are an expert programmer. Your task is to revise a piece of code based on specific feedback.
You will be given the feedback, the current code, and some search results for context.
Your output MUST be ONLY the complete, updated code for the file. Do NOT include any explanations, markdown, or any text other than the code itself.

**Search Results:**
{search_results}
"""
        user_message = f"**Revision Feedback:**\n{feedback}\n\n**Current Code:**\n```\n{current_code}\n```\n\nPlease provide the complete, revised code for the file."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self.llm.generate_completion(messages, temperature=0.1)
