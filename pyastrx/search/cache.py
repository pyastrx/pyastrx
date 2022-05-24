from pathlib import Path
from typing import Dict, Tuple

from pyastrx.data_typing import FileInfo


class Cache:
    """
    A file cache for pyastrx.
    """
    def __init__(self) -> None:
        self._cache: Dict[str, FileInfo] = {}

    def update(self, filename: str) -> Tuple[bool, float]:
        """ If the cache should be updated or not
        """
        file_path = Path(filename)
        if not file_path.exists():
            raise FileNotFoundError(f"File '{filename}' not found.")

        last_modified = file_path.stat().st_mtime
        if filename not in self._cache.keys():
            return True, last_modified
        info = self.get(filename)
        # check cache
        if info.last_modified == last_modified:
            return False, last_modified
        return True, last_modified

    def get(self, filename: str) -> FileInfo:
        """
        Get a value from the cache.
        """
        return self._cache[filename]

    def set(self, filename: str, file_info: FileInfo) -> None:
        """
        Set a value in the cache.
        """
        self._cache[filename] = file_info