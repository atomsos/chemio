"""
CHEMIO
"""


__version__ = '1.3.0'
def version():
    return __version__

from .chemio import read, write, preview
