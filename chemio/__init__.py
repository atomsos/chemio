"""
GASEIO
"""


__version__ = '1.0.1'
def version():
    return __version__

from .chemio import read, write, preview
