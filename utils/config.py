import yaml
from pathlib import Path

def load_config():
    config_path = Path("config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_model_config(model_id: str):
    config = load_config()
    return config["models"].get(model_id, {})

def get_system_prompt():
    config = load_config()
    return config["system"]["prompt"] 