from agents.base_agent import BaseAgent
from typing import Dict, Any
from llm.openai_llm import OpenAILLM
import json
from tools.file_tools import read_file

class EvaluatorAgent(BaseAgent):
    def __init__(self, name: str = "Evaluator", role: str = "Code Quality & Correctness Inspector"):
        super().__init__(name, role)
        self.llm = OpenAILLM()

    def execute_task(self, task: Dict[str, Any]) -> str:
        if not self.llm:
            return "Error: EvaluatorAgent LLM is not initialized."

        goal = task.get("goal")
        file_path = task.get("file_path")
        requester = task.get("requester")

        if not goal or not file_path or not requester:
            return "Error: 'goal', 'file_path', and 'requester' are required for evaluation."

        print(f"[{self.name}] received evaluation request for '{file_path}' from '{requester}'.")

        code_to_evaluate = read_file(file_path)
        if code_to_evaluate.startswith("Error:"):
            self.send_message(requester, {"type": "evaluation_result", "status": "error", "feedback": code_to_evaluate, "file_path": file_path})
            return code_to_evaluate

        evaluation_result = self._evaluate_code(goal, code_to_evaluate, file_path)
        
        # Send the evaluation back to the requester
        self.send_message(requester, evaluation_result)
        
        return f"Evaluation complete for '{file_path}'. Results sent to '{requester}'."

    def _evaluate_code(self, goal: str, code: str, file_path: str) -> Dict[str, Any]:
        system_prompt = """
You are an expert code evaluator. Your task is to assess a given piece of code based on a user's goal.
Your evaluation MUST be in a JSON format. The JSON object must have two keys:
1.  "status": (string) Either "approved" or "requires_revision".
2.  "feedback": (string) If the status is "approved", provide a brief confirmation message. If "requires_revision", provide clear, specific, and constructive feedback on what needs to be changed to meet the goal.

Evaluation criteria:
- Readability: Is the code reader friendly?
- Adherence: Does the code follow the specific requirements mentioned in the goal?

Example 1 (Approved):
Goal: "Create a Python function that adds two numbers."
Code: "def add(a, b): return a + b"
Your JSON Output:
{
    "status": "approved",
    "feedback": "The code correctly implements the function to add two numbers."
}

Example 2 (Requires Revision):
Goal: "Create a Python function that adds two numbers."
Code: "def add(a, b): return a * b"
Your JSON Output:
{
    "status": "requires_revision",
    "feedback": "The code incorrectly multiplies the numbers instead of adding them. Please change the operator from '*' to '+'."
}
"""
        user_message = f"Please evaluate the following code based on the user's goal.\n\n**Goal:** {goal}\n\n**Code:**\n```\n{code}\n```"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response_str = self.llm.generate_completion(
                messages,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            print(f"[{self.name}] Raw LLM Evaluation Response:\n{response_str}\n")
            evaluation = json.loads(response_str)
            evaluation["type"] = "evaluation_result" 
            evaluation["file_path"] = file_path
            return evaluation
        except json.JSONDecodeError as e:
            print(f"[{self.name}] Failed to parse LLM evaluation response as JSON: {e}")
            return {"type": "evaluation_result", "status": "error", "feedback": f"Failed to parse LLM response: {e}", "file_path": file_path}
        except Exception as e:
            print(f"[{self.name}] Error during evaluation: {e}")
            return {"type": "evaluation_result", "status": "error", "feedback": f"An unexpected error occurred during evaluation: {e}", "file_path": file_path}

    def receive_message(self, sender: str, message: Dict[str, Any]):
        if message.get("type") == "evaluation_request":
            self.execute_task(message)
        else:
            super().receive_message(sender, message)
