"""Data loading and preprocessing for Letterboxd CSV files."""
import pandas as pd
import os
from typing import Dict, Callable, Optional


def load_all_data(data_dir: str, on_progress: Optional[Callable] = None) -> Dict[str, pd.DataFrame]:
    """Load all Letterboxd CSV files from a directory."""
    data = {}

    def report(msg: str, pct: float):
        if on_progress:
            on_progress(msg, pct)

    report("Loading watched.csv...", 0.0)
    data['watched'] = _load_csv(data_dir, 'watched.csv')

    report("Loading diary.csv...", 0.2)
    data['diary'] = _load_csv(data_dir, 'diary.csv')

    report("Loading ratings.csv...", 0.4)
    data['ratings'] = _load_csv(data_dir, 'ratings.csv')

    report("Loading watchlist.csv...", 0.6)
    data['watchlist'] = _load_csv(data_dir, 'watchlist.csv')

    report("Loading likes...", 0.8)
    data['likes'] = _load_csv(data_dir, 'likes/films.csv', required=False)

    # Preprocess
    _preprocess_data(data)

    report(f"Loaded {len(data['watched'])} films", 1.0)
    return data


def _load_csv(data_dir: str, filename: str, required: bool = True) -> pd.DataFrame:
    """Load a single CSV file."""
    filepath = os.path.join(data_dir, filename)

    if not os.path.exists(filepath):
        if required:
            raise FileNotFoundError(f"Required file not found: {filepath}")
        return pd.DataFrame()

    try:
        return pd.read_csv(filepath)
    except Exception as e:
        if required:
            raise Exception(f"Error loading {filename}: {e}")
        return pd.DataFrame()


def _preprocess_data(data: Dict[str, pd.DataFrame]):
    """Preprocess and clean data."""
    # Convert dates
    if 'diary' in data and not data['diary'].empty:
        data['diary']['Watched Date'] = pd.to_datetime(
            data['diary']['Watched Date'],
            errors='coerce'
        )

    # Clean up year columns
    for key in ['watched', 'diary', 'ratings', 'watchlist']:
        if key in data and not data[key].empty and 'Year' in data[key].columns:
            data[key]['Year'] = pd.to_numeric(
                data[key]['Year'],
                errors='coerce'
            ).fillna(0).astype(int)
