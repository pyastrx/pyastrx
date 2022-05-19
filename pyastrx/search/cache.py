import os
import json
from pathlib import Path


class Cache:
    """
    A file cache for pyastrx.
    """
    def __init__(self, cache_dir="/tmp/pyastrx"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(self.cache_dir, 'cache.json')
        self.cache = {}

    def load(self):
        """
        Load the cache.
        """
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)

    def save(self):
        """
        Save the cache.
        """
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def update(self, filename):
        """
        Get a value from the cache.
        """
        file_path = Path(filename)
        if not file_path.exists():
            raise FileNotFoundError(f"File '{filename}' not found.")

        last_modified = file_path.stat().st_mtime
        info = self.cache.get(filename, False)
        if not info:
            return False, last_modified

        # check cache
        if info.last_modified == last_modified:
            return info, last_modified
        return False, last_modified

    def get(self, filename):
        """
        Get a value from the cache.
        """
        return self.cache.get(filename)

    def set(self, key, value):
        """
        Set a value in the cache.
        """
        self.cache[key] = value