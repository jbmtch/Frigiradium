from dotenv import load_dotenv
import os
import django

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()