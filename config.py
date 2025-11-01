import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_USER = os.getenv("DB_USER", "trading_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "your_passowrd")
    DB_NAME = os.getenv("DB_NAME", "trading_system")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    # API Keys
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
    FINNHUB_KEY = os.getenv("FINNHUB_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

