"""LLM Client with support for OpenAI and Ollama"""

import os
import json
import requests
from typing import Dict, Any, Optional
from openai import OpenAI


class LLMClient:
    """Unified LLM client supporting OpenAI and Ollama"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        elif self.provider == "ollama":
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.provider}")
    
    def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        response_format: Optional[str] = None
    ) -> str:
        """
        Get chat completion from configured LLM provider.
        
        Args:
            system_prompt: System message
            user_prompt: User message
            temperature: Sampling temperature
            response_format: Optional "json_object" for structured output
            
        Returns:
            Response text from LLM
        """
        if self.provider == "openai":
            return self._openai_completion(system_prompt, user_prompt, temperature, response_format)
        else:  # ollama
            return self._ollama_completion(system_prompt, user_prompt, temperature, response_format)
    
    def _openai_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        response_format: Optional[str]
    ) -> str:
        """OpenAI-specific completion"""
        kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        
        if response_format == "json_object":
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def _ollama_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        response_format: Optional[str]
    ) -> str:
        """Ollama-specific completion"""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        # Handle JSON format request for Ollama
        if response_format == "json_object":
            system_prompt = f"{system_prompt}\n\nIMPORTANT: You must respond with valid JSON only. No other text."
            payload["messages"][0]["content"] = system_prompt
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result["message"]["content"]
