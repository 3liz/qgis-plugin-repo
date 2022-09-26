from pathlib import Path
from typing import Union
from urllib.parse import urlparse

__copyright__ = 'Copyright 2022, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


def is_url(uri: Union[Path, str]) -> bool:
    """ Check if the URI can be a URL. """
    if isinstance(uri, Path):
        return False

    path = Path(uri)
    if path.exists():
        return False

    # noinspection PyBroadException
    try:
        urlparse(uri)
        return True
    except Exception:
        return False
