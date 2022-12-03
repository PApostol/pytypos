"""pytypos module"""

from typing import List

import enchant

from .__info__ import (
    __author__,
    __author_email__,
    __bugtrack_url__,
    __description__,
    __license__,
    __maintainer__,
    __title__,
    __url__,
    __version__,
)
from ._pytypos import Pytypos


def available_languages() -> List[str]:
    """Returns a list with the available language dictionaries found on the host system

    Returns:
        List[str]: available language dictionaries found
    """
    return enchant.list_languages()


__all__ = ['Pytypos', 'available_languages']
