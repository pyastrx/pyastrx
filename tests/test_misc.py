from pathlib import Path
from pyastrx.folder_utils import get_location_and_create


def test_get_location_and_create():
    """Test the get_location_and_create function."""
    test_misc = Path("tests/test_misc.py")
    base_location = test_misc.parent
    filename = "test_misc.py"
    location = get_location_and_create(base_location, filename, extension="")
    assert location.exists()

    test_wrong = Path("tests/test_wrong.py")
    base_location = test_wrong.parent
    filename = "test_wrong.py"
    location = get_location_and_create(base_location, filename, extension="")
    assert not location.exists()
