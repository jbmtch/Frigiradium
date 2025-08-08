# env_debug.py
import os
from dotenv import load_dotenv

dotenv_path = os.path.abspath(".env")
print("Looking for .env at:", dotenv_path)
load_dotenv(dotenv_path=dotenv_path)

print("DB_NAME:", os.getenv("DB_NAME"))
