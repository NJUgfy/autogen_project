from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from agent_manager import AgentManager

class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.manager: AgentManager = None

    def set_manager(self, manager: AgentManager):
        self.manager = manager

    def execute_task(self, task: Dict[str, Any]) -> str:
        raise NotImplementedError

    def send_message(self, recipient: str, message: Dict[str, Any]):
        if self.manager:
            self.manager.send_message(recipient, message, self.name)
        else:
            print(f"[{self.name}] cannot send message: manager not set.")

    def receive_message(self, sender: str, message: Dict[str, Any]):
        print(f"[{self.name}] received message from [{sender}]: {message}")
        self.execute_task(message)
