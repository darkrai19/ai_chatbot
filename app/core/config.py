from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://dev_user_ro:user_ro_dev@sso.wibix.ai:5432/suronex-latest"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL_NAME: str = "llama3.2:3b"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()