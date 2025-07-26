from pydantic import BaseSettings

class Settings(BaseSettings):
    AUTHORIZE_URL_BASE: str
    RECVUE_API_BASE_URL: str
    RECVUE_API_TOKEN: str
    TIMEOUT: int = 30
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()