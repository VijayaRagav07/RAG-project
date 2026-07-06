import os
import json
import requests
import google.generativeai as genai
from typing import Generator, List, Dict, Any

class LLMInterface:
    def __init__(self, provider: str = "gemini", api_key: str = None, model: str = None, ollama_url: str = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.ollama_url = ollama_url or "http://localhost:11434"
        
        if self.provider == "gemini":
            if self.api_key:
                genai.configure(api_key=self.api_key)
            self.model_name = model or "gemini-1.5-flash"
        elif self.provider == "ollama":
            self.model_name = model or "llama3"
        else:
            self.model_name = "mock"

    def generate_response(self, prompt: str, temperature: float = 0.7) -> str:
        """Generates a full synchronous response from the selected LLM provider."""
        if self.provider == "gemini":
            if not self.api_key:
                raise ValueError("Gemini API Key is not set. Please provide it in the sidebar or a .env file.")
            try:
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(temperature=temperature)
                )
                return response.text
            except Exception as e:
                print(f"Error calling Gemini LLM: {e}")
                raise e
                
        elif self.provider == "ollama":
            try:
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                }
                response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=30)
                response.raise_for_status()
                return response.json().get("response", "")
            except Exception as e:
                print(f"Error calling Ollama LLM: {e}")
                raise e
                
        elif self.provider == "mock":
            return f"Mock response for offline testing. Prompt received: '{prompt[:60]}...'"
            
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def generate_response_stream(self, prompt: str, temperature: float = 0.7) -> Generator[str, None, None]:
        """Generates a streaming response token by token from the selected LLM provider."""
        if self.provider == "gemini":
            if not self.api_key:
                raise ValueError("Gemini API Key is not set. Please provide it in the sidebar or a .env file.")
            try:
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(temperature=temperature),
                    stream=True
                )
                for chunk in response:
                    # Some chunks might have empty text if blocked or finished
                    if chunk.text:
                        yield chunk.text
            except Exception as e:
                print(f"Error streaming Gemini LLM: {e}")
                raise e
                
        elif self.provider == "ollama":
            try:
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": temperature
                    }
                }
                response = requests.post(f"{self.ollama_url}/api/generate", json=payload, stream=True, timeout=30)
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        chunk_data = json.loads(line.decode("utf-8"))
                        text_chunk = chunk_data.get("response", "")
                        if text_chunk:
                            yield text_chunk
            except Exception as e:
                print(f"Error streaming Ollama LLM: {e}")
                raise e
                
        elif self.provider == "mock":
            words = f"This is a mocked streaming response to verify the UI. Received prompt: {prompt[:40]}...".split()
            import time
            for word in words:
                yield word + " "
                time.sleep(0.08)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
