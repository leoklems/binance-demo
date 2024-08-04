from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

# Config will be read from environment variables and/or ".env" files.
config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)

BINANCE_API_KEY = config("BINANCE_API_KEY", default="")
BINANCE_API_SECRET = config("BINANCE_API_SECRET", default="")
