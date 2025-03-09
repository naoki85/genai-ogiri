from anthropic import Anthropic
import os
from models.base_model import BaseAIModel
from models.answer import Answer
from utils.config import get_model_config

class ClaudeModel(BaseAIModel):
    def __init__(self, system_prompt: str, display_name: str = None):
        config = get_model_config("claude")
        super().__init__(system_prompt, display_name or config["display_name"])
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model_name = "claude"
        self.config = config
    
    def stream_response(self, theme: str, placeholder) -> Answer:
        content = ""
        with self.client.messages.stream(
            model=self.config["model_name"],
            max_tokens=self.config["max_tokens"],
            temperature=self.config["temperature"],
            system=self.system_prompt,
            messages=[{
                "role": "user",
                "content": f"以下のお題で面白い回答を考えてください。\nお題: {theme}\n"
            }]
        ) as stream:
            for text in stream.text_stream:
                content += text
                placeholder.markdown(self.format_message(content + "▌"))
        
        placeholder.markdown(self.format_message(content))
        return Answer(round=1, model=self.model_name, content=content)
