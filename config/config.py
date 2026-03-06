from pydantic import BaseSettings
import os


class Config(BaseSettings):
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SELLER_SERVICE_BASE_URL: str = os.getenv("SELLER_SERVICE_BASE_URL")
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "100"))
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    TOKEN_EXPIRY_TIME: float = float(os.getenv("TOKEN_EXPIRY_TIME", "20"))
    OPEN_AI_KEY: str = os.getenv("OPEN_AI_KEY")
    SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")
    WEAVIATE_BASE_URL: str = os.getenv("WEAVIATE_BASE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Config()
