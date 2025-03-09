from openai import OpenAI
import os
from models.base_model import BaseAIModel
from models.answer import Answer
from utils.config import get_model_config

class DeepSeekModel(BaseAIModel):
    def __init__(self, system_prompt: str, display_name: str = None):
        config = get_model_config("deepseek")
        super().__init__(system_prompt, display_name or config["display_name"])
        self.client = OpenAI(
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY")
        )
        self.model_name = "deepseek"
        self.config = config
    
    def stream_response(self, theme: str, placeholder) -> Answer:
        content = ""
        stream = self.client.chat.completions.create(
            model=self.config["model_name"],
            temperature=self.config["temperature"],
            max_tokens=self.config["max_tokens"],
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"以下のお題で面白い回答を考えてください。\nお題: {theme}\n"}
            ],
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
                placeholder.markdown(self.format_message(content + "▌"))
        
        placeholder.markdown(self.format_message(content))
        return Answer(round=1, model=self.model_name, content=content) 