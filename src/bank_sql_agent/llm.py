"""
راه‌اندازی مدل زبانی (LLM) مورد استفاده در تمام زنجیره‌ها.
"""

from langchain.chat_models import init_chat_model
import os
from pathlib import Path
from dotenv import load_dotenv

# Navigate up 3 levels from llm.py to find the root 'bank-sql-agent' folder
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def init_llm(model_name: str = None, provider: str = "openai", temperature: float = 0):
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "glm-5.3-flash-free")
    return init_chat_model(
        model=model_name,
        model_provider=provider,
        temperature=temperature,
        max_tokens=1000,
        timeout=60,
        max_retries=3,
    )


llm = init_llm()
