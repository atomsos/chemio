"""
CHEMIO
"""


__version__ = '1.4.5'
def version():
    return __version__

from .chemio import read, write, preview
