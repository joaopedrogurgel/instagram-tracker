import os

class Config:
    MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "25"))
    MAX_ROWS = int(os.getenv("MAX_ROWS", "500000"))
    RATE_LIMIT = os.getenv("RATE_LIMIT", "20/minute")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    API_VERSION = os.getenv("API_VERSION", "1.1.0")

config = Config()
