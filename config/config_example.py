from pydantic import BaseSettings


class Config(BaseSettings):
    MYSQL_USER: str = "your_db_user"
    MYSQL_PASSWORD: str = "your_db_password"
    MYSQL_DATABASE: str = "your_db_name"
    MYSQL_HOST: str = "your_db_host"
    MYSQL_PORT: str = "your_db_port"
    DATABASE_URL: str = "mysql://your_db_user:your_db_password@localhost:3306/your_db_name"
    SELLER_SERVICE_BASE_URL: str = "https://example-seller-service.com/api"
    REDIS_HOST: str = "your_redis_host"
    REDIS_PORT: int = "your_redis_port"
    REDIS_TTL: int = 100  # in seconds
    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRY_TIME: float = 20 # in minutes
    OPEN_AI_KEY: str = "sk-your-openai-key"
    SYSTEM_PROMPT: str = "You are a helpful assistant."
    WEAVIATE_BASE_URL: str = "your weaviate base url"