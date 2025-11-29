from agents.base_agent import BaseAgent
from typing import Dict, Any
from llm.openai_llm import OpenAILLM
import json

class PlannerAgent(BaseAgent):
    def __init__(self, name: str = "Planner", role: str = "Task Decomposition and Orchestration Specialist"):
        super().__init__(name, role)
        self.llm = OpenAILLM()
        self.plan = []
        self.goal = ""
        self.search_history = []
        self.current_task_id = -1
        self.evaluation_history = []

    def execute_task(self, task: Dict[str, Any]) -> str:
        self.goal = task.get("goal")
        if not self.goal:
            return "Error: 'goal' is required for planning."

        print(f"[{self.name}] received new goal: {self.goal}")
        self._generate_and_send_plan()

        return f"Plan generation started for goal: {self.goal}"
    
    def _generate_and_send_plan(self):
        plan_str = self._generate_plan(self.goal, self.search_history)
        try:
            self.plan = json.loads(plan_str)
            print(f"[{self.name}] generated plan:\n{json.dumps(self.plan, indent=2)}")
            self._send_next_task()
        except json.JSONDecodeError as e:
            print(f"[{self.name}] Failed to parse plan as JSON: {e}")

    def _generate_plan(self, goal: str, search_history: list = []) -> str:
        system_prompt = """
You are an expert planner. Your task is to break down a user's goal into a series of smaller, manageable tasks.
You can use a 'search' action to gather information if the goal is ambiguous.
Your output MUST be a JSON array of objects. Each object represents a task and must have the following keys:
- "task_id": (integer) A unique identifier for the task, starting from 1.
- "action": (string) The action to be performed. Must be one of: "search", "write_code", "evaluate_code", "finish".
- "description": (string) A clear and concise description of the task.
- "file_path": (string) The full path to the file relevant to the task. For 'search' and 'finish' actions, this can be an empty string.
- "query": (string, optional) The search query for the 'search' action.
- "status": (string) The initial status, always "pending".

For each piece of functionality, create a 'write_code' task followed by an 'evaluate_code' task.
If the goal is ambiguous, start with a 'search' task.
The very last step MUST be an action of type 'finish'.

Example:
Goal: "Create a complete front-end for an arxiv cs daily website. This includes creating data.js for paper data, a script.js for DOM manipulation, an index.html for the main page, a category.html for filtered views, a detail.html for paper details, and a style.css for styling."

Your JSON Output:
[
    {
        "task_id": 1,
        "action": "write_code",
        "description": "Create the data.js file with sample paper data. It should be an array of javascript objects, each with fields like id, title, authors, abstract, etc.",
        "file_path": "output/arxiv_cs_daily/data.js",
        "status": "pending"
    },
    {
        "task_id": 2,
        "action": "evaluate_code",
        "description": "Evaluate data.js to ensure it contains valid javascript and the data structure is correct.",
        "file_path": "output/arxiv_cs_daily/data.js",
        "status": "pending"
    },
    {
        "task_id": 3,
        "action": "write_code",
        "description": "Create the style.css file with some basic styling for the website.",
        "file_path": "output/arxiv_cs_daily/style.css",
        "status": "pending"
    },
    {
        "task_id": 4,
        "action": "evaluate_code",
        "description": "Evaluate style.css to ensure it contains valid CSS.",
        "file_path": "output/arxiv_cs_daily/style.css",
        "status": "pending"
    },
    {
        "task_id": 5,
        "action": "write_code",
        "description": "Create the index.html file. It should have a list of CS categories and link to the category pages.",
        "file_path": "output/arxiv_cs_daily/index.html",
        "status": "pending"
    },
    {
        "task_id": 6,
        "action": "evaluate_code",
        "description": "Evaluate index.html for valid HTML structure and correct links.",
        "file_path": "output/arxiv_cs_daily/index.html",
        "status": "pending"
    },
    {
        "task_id": 7,
        "action": "write_code",
        "description": "Create the category.html file. It should display a filtered list of papers based on a category parameter.",
        "file_path": "output/arxiv_cs_daily/category.html",
        "status": "pending"
    },
    {
        "task_id": 8,
        "action": "evaluate_code",
        "description": "Evaluate category.html for valid HTML structure and correct filtering logic.",
        "file_path": "output/arxiv_cs_daily/category.html",
        "status": "pending"
    },
    {
        "task_id": 9,
        "action": "write_code",
        "description": "Create the detail.html file. It should display the details of a single paper.",
        "file_path": "output/arxiv_cs_daily/detail.html",
        "status": "pending"
    },
    {
        "task_id": 10,
        "action": "evaluate_code",
        "description": "Evaluate detail.html for valid HTML structure and correct display of paper details.",
        "file_path": "output/arxiv_cs_daily/detail.html",
        "status": "pending"
    },
    {
        "task_id": 11,
        "action": "write_code",
        "description": "Create the script.js file. It should contain functions to load and render paper data from data.js, handle category filtering, and display paper details.",
        "file_path": "output/arxiv_cs_daily/script.js",
        "status": "pending"
    },
    {
        "task_id": 12,
        "action": "evaluate_code",
        "description": "Evaluate script.js for valid javascript and correct functionality across all pages.",
        "file_path": "output/arxiv_cs_daily/script.js",
        "status": "pending"
    },
    {
        "task_id": 13,
        "action": "finish",
        "description": "Summarize the project and evaluation results.",
        "file_path": "",
        "status": "pending"
    }
]
"""
        history_context = ""
        if search_history:
            history_str = json.dumps(search_history, indent=2)
            history_context = f"\n\nHere is the search history for your reference:\n{history_str}"
            
        user_message = f"Please generate a plan for the following goal:\n\n**Goal:** {goal}{history_context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self.llm.generate_completion(
            messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )

    def _send_next_task(self):
        if not self.plan:
            print(f"[{self.name}] Plan is empty or complete.")
            return

        next_task = self.plan.pop(0)
        self.current_task_id = next_task.get("task_id")
        action = next_task.get("action")

        if action == "search":
            next_task["type"] = "search_request"
            next_task["requester"] = self.name
            self.send_message("Searcher", next_task)
            print(f"[{self.name}] Sent task {self.current_task_id} ({action}) to Searcher.")
        elif action == "write_code":
            next_task["type"] = "coding_task"
            self.send_message("Coder", next_task)
            print(f"[{self.name}] Sent task {self.current_task_id} ({action}) to Coder.")
        elif action == "evaluate_code":
            next_task["type"] = "evaluation_request"
            next_task["requester"] = self.name
            next_task["goal"] = next_task["description"]
            self.send_message("Evaluator", next_task)
            print(f"[{self.name}] Sent task {self.current_task_id} ({action}) to Evaluator.")
        elif action == "finish":
            self._summarize_and_finish()
        else:
            print(f"[{self.name}] Unknown action: {action}")
            self._send_next_task()

    def _summarize_and_finish(self):
        print(f"[{self.name}] Summarizing and finishing project.")
        
        summary_prompt = "You are a project manager. Based on the following evaluation history, provide a concise summary of the project's development process and the final outcome."
        
        history_str = json.dumps(self.evaluation_history, indent=2)
        
        messages = [
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": f"Evaluation History:\n{history_str}"}
        ]
        
        summary = self.llm.generate_completion(messages, temperature=0.5)
        
        print("\n" + "="*50)
        print(" " * 20 + "PROJECT SUMMARY")
        print("="*50)
        print(summary)
        print("="*50)
        print(f"[{self.name}] Project finished.")


    def receive_message(self, sender: str, message: Dict[str, Any]):
        if message.get("type") == "task_complete" and sender == "Coder":
            print(f"[{self.name}] received task completion for task {self.current_task_id} from Coder.")
            self._send_next_task()
        elif message.get("type") == "evaluation_result":
            status = message.get("status")
            self.evaluation_history.append(message)
            print(f"[{self.name}] received evaluation result for task {self.current_task_id} from Evaluator: {status}")
            if status == "approved":
                self._send_next_task()
            elif status == "requires_revision":
                revision_task = {
                    "task_id": self.current_task_id,
                    "action": "write_code",
                    "type": "evaluation_result",
                    "description": "Revise code based on feedback",
                    "file_path": message.get("file_path"),
                    "status": "requires_revision",
                    "feedback": message.get("feedback")
                }
                self.plan.insert(0, self.plan.pop(0))
                self.plan.insert(0, revision_task)
                self._send_next_task()
        elif message.get("type") == "search_result":
            print(f"[{self.name}] received search result for task {self.current_task_id} from Searcher.")
            self.search_history.append(message.get("results"))
            self._generate_and_send_plan()
        else:
            super().receive_message(sender, message)
