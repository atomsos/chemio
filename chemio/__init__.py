"""
CHEMIO
"""

from .main import read, write, preview, convert

__version__ = '1.6.1'
def version():
    return __version__


def _setdebug():
    from . import main
    main._setdebug()
