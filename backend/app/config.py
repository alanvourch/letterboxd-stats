"""Configuration settings for the web app."""
import os
from dotenv import load_dotenv

load_dotenv()

# TMDB API
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/"
TMDB_RATE_LIMIT = int(os.getenv("TMDB_RATE_LIMIT", "50"))

# Cache
CACHE_FILE = os.getenv("CACHE_FILE", "./data/tmdb_cache.json")
CACHE_EXPIRY_DAYS = int(os.getenv("CACHE_EXPIRY_DAYS", "30"))

# Poster settings
POSTER_SIZE = os.getenv("POSTER_SIZE", "w185")

# Stats settings
TOP_ACTORS_COUNT = int(os.getenv("TOP_ACTORS_COUNT", "20"))
TOP_DIRECTORS_COUNT = int(os.getenv("TOP_DIRECTORS_COUNT", "15"))
TOP_GENRES_COUNT = int(os.getenv("TOP_GENRES_COUNT", "10"))

# Web app settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,https://letterboxd-stats-two.vercel.app").split(",")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
JOB_EXPIRY_MINUTES = int(os.getenv("JOB_EXPIRY_MINUTES", "60"))
RATE_LIMIT = os.getenv("RATE_LIMIT", "5/hour")
