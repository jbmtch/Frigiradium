import os
import django
from dotenv import load_dotenv

# # Build absolute path to .env file two levels up from backend/conftest.py
# dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))

# print("Loading .env from:", dotenv_path)  # ✅ Add this debug line

# load_dotenv(dotenv_path=dotenv_path)

# # Confirm variable loaded
# print("Loaded DB_NAME:", os.getenv("DB_NAME"))  # ✅ Should not be None

# # Set Django settings
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
# django.setup()

import os
import django
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
print(f"Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

print("DB_NAME in conftest.py:", os.getenv("DB_NAME"))  # 👈 This MUST work

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

