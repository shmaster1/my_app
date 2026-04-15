import ssl
from databases import Database
from config.config import Config

config = Config()

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

database = Database(
    config.DATABASE_URL.replace("?ssl=true", ""),
    ssl=ssl_ctx
)