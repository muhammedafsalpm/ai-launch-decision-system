"""Base agent class with shared functionality"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from utils.llm_client import LLMClient


class BaseAgent(ABC):
    """Base class for all agents with built-in logging"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.llm = LLMClient()
    
    def log(self, message: str, tool_call: str = None):
        """Logging for traceability requirement"""
        prefix = f"[TRACE] {self.name}"
        if tool_call:
            prefix += f" → TOOL:{tool_call}"
        print(f"{prefix} | {message}")
    
    def call_llm(self, system_prompt: str, user_prompt: str, response_format: str = None) -> str:
        """Wrapper for LLM calls with provider abstraction"""
        return self.llm.chat_completion(system_prompt, user_prompt, response_format=response_format)
    
    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Each agent must implement this method"""
        pass
