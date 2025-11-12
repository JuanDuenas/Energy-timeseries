import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "timescaledb")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "energydb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

API_URL = os.getenv("API_URL", "http://api:8000/data")
INTERVAL = int(os.getenv("INTERVAL", "5"))  # segundos entre lecturas simuladas
