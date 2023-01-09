from pathlib import Path


def get_location_and_create(
        base_location: str, filename: str, extension: str = ".txt") -> Path:
    """Create a folder if it doesn't exist and return the path

    Args:
        base_location: The base location
        filename: The filename
    Returns:
        The path

    """
    current_folder = Path(".").resolve()
    export_folder = Path(base_location).resolve()
    path_location = Path(filename).resolve()
    suffix = path_location.suffix
    new_filename = path_location.name
    location = path_location.parent.relative_to(current_folder)
    export_location = export_folder/location/new_filename
    export_location = export_location.with_suffix(f"{suffix}{extension}")

    if not export_location.parent.exists():
        export_location.parent.mkdir(parents=True)

    return export_location
