import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Configuration
USE_GPT = os.getenv("USE_GPT", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

# Model Settings
DEFAULT_TEMPERATURE = 0.4
OLLAMA_MODEL = "llama3.2"

# Analysis Settings
DEFAULT_CUTOFF_SCORE = 80
MAX_WORKERS = 5

# Embedding Settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200