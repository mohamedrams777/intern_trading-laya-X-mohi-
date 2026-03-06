import os
from dotenv import load_dotenv
import pathlib

load_dotenv()

basedir = pathlib.Path(__file__).resolve().parent

class Config:
    # Prefer explicit DATABASE_URL if provided
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # If explicit Postgres env vars are provided, use Postgres
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")

        if DB_USER and DB_PASSWORD and DB_NAME and DB_HOST and DB_PORT:
            SQLALCHEMY_DATABASE_URI = (
                f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            )
        else:
            # Fallback to a local SQLite file so the app can run without Postgres
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'data.sqlite3'}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    # API Keys
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
    FINNHUB_KEY = os.getenv("FINNHUB_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

