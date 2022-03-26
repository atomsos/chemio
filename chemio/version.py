__version__ = '1.6.9'
LOGLEVEL_ENV = "CHEMIO_LOGLEVEL"


def version():
    return __version__


def set_loglevel(loglevel):
    os.environ[LOGLEVEL_ENV] = str(loglevel)
    main.logger = modlog.getLogger(main.__name__)
