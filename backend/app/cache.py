"""Thread-safe TMDB cache manager."""
import json
import os
import threading
import time
from typing import Dict, Any
from app import config


class TMDBCache:
    """Shared TMDB cache with periodic persistence."""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._dirty = False
        self._last_save = time.time()
        self._new_entries = 0
        self._load()

    def _load(self):
        """Load cache from disk."""
        if os.path.exists(config.CACHE_FILE):
            try:
                with open(config.CACHE_FILE, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                print(f"Loaded {len(self._data)} cached films")
            except Exception as e:
                print(f"Failed to load cache: {e}")
                self._data = {}

    def save(self):
        """Save cache to disk."""
        with self._lock:
            if not self._dirty:
                return
            try:
                os.makedirs(os.path.dirname(config.CACHE_FILE) or '.', exist_ok=True)
                with open(config.CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self._data, f)
                self._dirty = False
                self._new_entries = 0
                self._last_save = time.time()
                print(f"Saved {len(self._data)} films to cache")
            except Exception as e:
                print(f"Failed to save cache: {e}")

    def mark_dirty(self, new_count: int = 1):
        """Mark cache as dirty and maybe auto-save."""
        self._dirty = True
        self._new_entries += new_count
        # Auto-save every 50 entries or 2 minutes
        if self._new_entries >= 50 or (time.time() - self._last_save) > 120:
            self.save()

    def force_save(self):
        """Force save regardless of dirty state."""
        self._dirty = True
        self.save()

    def get_data(self) -> Dict[str, Any]:
        """Get reference to cache dict for enricher."""
        return self._data

    def size(self) -> int:
        """Return cache size."""
        return len(self._data)
