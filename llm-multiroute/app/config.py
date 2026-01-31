import os


class Settings:
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8080"))
    APP_NAME: str = os.getenv("APP_NAME", "llm-multiroute")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "https://ollama.com")
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    OLLAMA_API_KEY: str = os.getenv("OLLAMA_API_KEY", "")

    # Per-route model assignments (must be available on Ollama cloud)
    OLLAMA_MODEL_CLASSIFY: str = os.getenv("OLLAMA_MODEL_CLASSIFY", "gemma3:4b")
    OLLAMA_MODEL_SENTIMENT: str = os.getenv("OLLAMA_MODEL_SENTIMENT", "ministral-3:3b")
    OLLAMA_MODEL_SUMMARIZE: str = os.getenv("OLLAMA_MODEL_SUMMARIZE", "ministral-3:8b")
    OLLAMA_MODEL_INTENT: str = os.getenv("OLLAMA_MODEL_INTENT", "gemma3:12b")


settings = Settings()
