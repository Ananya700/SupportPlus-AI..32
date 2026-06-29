from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    FIRECRAWL_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "phi3"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    PORT: int = 8000
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.GEMINI_API_KEY == "your_gemini_api_key_here":
            self.GEMINI_API_KEY = ""
        if self.FIRECRAWL_API_KEY == "your_firecrawl_api_key_here":
            self.FIRECRAWL_API_KEY = ""
            
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
