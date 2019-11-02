"""
CHEMIO
"""

import os
from .main import read, write, preview, convert

__version__ = '1.6.5'
LOGLEVEL_ENV = "CHEMIO_LOGLEVEL"


def version():
    return __version__


def set_loglevel(loglevel):
    os.environ[LOGLEVEL_ENV] = str(loglevel)
