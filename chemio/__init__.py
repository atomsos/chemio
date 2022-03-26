"""
CHEMIO
"""

import os
import modlog
import warnings
try:
    import gaseio
    from gaseio import read, write
    from gaseio import read_preview, write_preview, preview, get_write_content
    from gaseio import list_supported_write_formats
    from gaseio import __version__, version
    __string__ = "Use gaseio instead"
    __version__ = 'gaseio:' + __version__
    # print(ImportWarning(__string__))
    warnings.warn(__string__)
except Exception as e:
    from . import main
    from .main import read, write, preview, convert
    from .molecule import get_molecule
    from .version import __version__, version, set_loglevel, LOGLEVEL_ENV
