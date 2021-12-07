"""pytypos module"""

from ._pytypos import Pytypos
from .__info__ import (
    __title__,
    __author__,
    __author_email__,
    __maintainer__,
    __license__,
    __version__,
    __description__,
    __url__,
    __bugtrack_url__,
)
from typing import List
import enchant


def available_languages() -> List[str]:
    """Returns a list with the available language dictionaries found on the host system

    Returns:
        List[str]: available language dictionaries found
    """
    return enchant.list_languages()


__all__ = ['Pytypos', 'available_languages']
