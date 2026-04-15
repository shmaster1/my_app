from pydantic import BaseSettings

class Config(BaseSettings):
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = ""
    MYSQL_HOST: str = ""
    MYSQL_PORT: str = ""
    DATABASE_URL: str = ""
    SELLER_SERVICE_BASE_URL: str = ""
    REDIS_HOST: str = ""
    REDIS_PORT: int = 0
    REDIS_TTL: int = 0
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    TOKEN_EXPIRY_TIME: float = 0
    OPEN_AI_KEY: str = ""
    SYSTEM_PROMPT: str = ""
    WEAVIATE_BASE_URL: str = ""
    WEAVIATE_API_KEY: str = ""
    NEXT_PUBLIC_API_URL: str = ""
    ANTHROPIC_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
#
# class Config(BaseSettings):
#     MYSQL_USER: str = os.getenv("MYSQL_USER")
#     MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
#     MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE")
#     MYSQL_HOST: str = os.getenv("MYSQL_HOST")
#     MYSQL_PORT: str = os.getenv("MYSQL_PORT")
#     DATABASE_URL: str = os.getenv("DATABASE_URL")
#     SELLER_SERVICE_BASE_URL: str = os.getenv("SELLER_SERVICE_BASE_URL")
#     REDIS_HOST: str = os.getenv("REDIS_HOST")
#     REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
#     REDIS_TTL: int = int(os.getenv("REDIS_TTL", "100"))
#     SECRET_KEY: str = os.getenv("SECRET_KEY")
#     ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
#     TOKEN_EXPIRY_TIME: float = float(os.getenv("TOKEN_EXPIRY_TIME", "20"))
#     OPEN_AI_KEY: str = os.getenv("OPEN_AI_KEY")
#     SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")
#     WEAVIATE_BASE_URL: str = os.getenv("WEAVIATE_BASE_URL", "")
#     WEAVIATE_API_KEY: str = os.getenv("WEAVIATE_API_KEY", "")
#     NEXT_PUBLIC_API_URL: str = os.getenv("NEXT_PUBLIC_API_URL", "")
#     ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
#
#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#
#
# settings = Config()
