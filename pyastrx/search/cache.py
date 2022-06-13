from pathlib import Path
from typing import Dict
import pickle

from pyastrx.data_typing import FileInfo


class Cache:
    """
    A file cache for pyastrx.
    """
    def __init__(self, file_cache: bool = True) -> None:
        self._cache: Dict[str, FileInfo] = {}
        self.file_cache = file_cache

    def _get_cache_location(self, file_path: Path) -> Path:
        """
        Get the location of the cache file.
        """
        root_folder = Path(".").absolute()
        file_cache = Path(
            f".pyastrx/files/{file_path.relative_to(root_folder)}").resolve()
        file_cache = file_cache.with_suffix(".cache")
        return file_cache

    def update(self, filename: str) -> bool:
        """ If the cache should be updated or not
        """
        file_path = Path(filename).absolute()
        if not file_path.exists():
            raise FileNotFoundError(f"File '{filename}' not found.")
        last_modified = file_path.stat().st_mtime
        file_cache = self._get_cache_location(file_path)
        if file_cache.exists() and self.file_cache:
            last_modified_cache = file_cache.stat().st_mtime
            if last_modified_cache < last_modified:
                return True
            file_info = pickle.load(open(file_cache, "rb"))
            self.set(filename, file_info, False)
            return False
        if filename in self._cache.keys():
            return False
        return True

    def get(self, filename: str) -> FileInfo:
        """
        Get a value from the cache.
        """
        return self._cache[filename]

    def set(
            self, filename: str,
            file_info: FileInfo, dump: bool = True) -> None:
        """
        Set a value in the cache.
        """
        self._cache[filename] = file_info
        if dump and self.file_cache:
            file_path = Path(filename).absolute()
            file_cache = self._get_cache_location(file_path)
            file_cache.parent.mkdir(parents=True, exist_ok=True)
            pickle.dump(file_info, open(file_cache, "wb"))
