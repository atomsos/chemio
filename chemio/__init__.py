"""
GASEIO
"""


__version__ = '1.2.0'
def version():
    return __version__

from .chemio import read, write, preview
