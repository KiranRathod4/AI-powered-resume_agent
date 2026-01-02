import os

USE_GPT = os.getenv("USE_GPT", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
