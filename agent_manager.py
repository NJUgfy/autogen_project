from typing import Dict, Any, List
from agents.base_agent import BaseAgent

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def add_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent
        agent.set_manager(self)
        print(f"[AgentManager] '{agent.name}' registered.")

    def send_message(self, recipient: str, message: Dict[str, Any], sender: str):
        if recipient in self.agents:
            print(f"[AgentManager] Routing message from '{sender}' to '{recipient}'.")
            self.agents[recipient].receive_message(sender, message)
        else:
            print(f"[AgentManager] Error: Recipient '{recipient}' not found.")

    def start_task(self, initial_goal: str, start_agent_name: str):
        if start_agent_name in self.agents:
            initial_task = {"goal": initial_goal}
            self.agents[start_agent_name].execute_task(initial_task)
        else:
            print(f"[AgentManager] Error: Start agent '{start_agent_name}' not found.")
