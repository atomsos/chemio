"""
CHEMIO
"""

import os
import modlog
from . import main
from .main import read, write, preview, convert
from .molecule import get_molecule

__version__ = '1.6.6'
LOGLEVEL_ENV = "CHEMIO_LOGLEVEL"


def version():
    return __version__


def set_loglevel(loglevel):
    os.environ[LOGLEVEL_ENV] = str(loglevel)
    main.logger = modlog.getLogger(main.__name__)
