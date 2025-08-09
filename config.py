# config.py
import os

# Ollama exposes an OpenAI-compatible endpoint at http://localhost:11434/v1
# AutoGen uses OpenAI-like config keys.
LLM_CONFIG = {
    "config_list": [{
        "model": os.getenv("OLLAMA_MODEL", "codellama:7b"),
        "api_key": os.getenv("OPENAI_API_KEY", "ollama"),    # dummy value works
        "base_url": os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
        "top_p": 0.95
    }],
     # Put tuning at the TOP level (not inside config_list)
    "temperature": 0.2,
    "timeout": 1200,
    "cache_seed": 42
}

# Conversation controls
MAX_TURNS = 20
