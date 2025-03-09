from google import genai
from google.genai import types
import os
from models.base_model import BaseAIModel
from models.answer import Answer
from utils.config import get_model_config

class GeminiModel(BaseAIModel):
    def __init__(self, system_prompt: str, display_name: str = None):
        config = get_model_config("gemini")
        super().__init__(system_prompt, display_name or config["display_name"])
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_name = "gemini"
        self.config = config
    
    def stream_response(self, theme: str, placeholder) -> Answer:
        content = ""
        response = self.client.models.generate_content_stream(
            model=self.config["model_name"],
            contents=[f"以下のお題で面白い回答を考えてください。\nお題: {theme}\n"],
            config=types.GenerateContentConfig(
                temperature=self.config["temperature"],
                max_output_tokens=self.config["max_tokens"],
                system_instruction=self.system_prompt,
            ),
        )
        
        for chunk in response:
            if chunk.text:
                content += chunk.text
                placeholder.markdown(self.format_message(content + "▌"))
        
        placeholder.markdown(self.format_message(content))
        return Answer(round=1, model=self.model_name, content=content)
