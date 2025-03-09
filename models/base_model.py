from abc import ABC, abstractmethod
from models.answer import Answer

class BaseAIModel(ABC):
    def __init__(self, system_prompt: str, display_name: str):
        self.system_prompt = system_prompt
        self.display_name = display_name
    
    def format_message(self, content: str) -> str:
        return f"**{self.display_name}**: {content}"
    
    @abstractmethod
    def stream_response(self, theme: str, placeholder) -> Answer:
        pass 