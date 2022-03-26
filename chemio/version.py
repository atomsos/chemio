__version__ = '2.0.0'
LOGLEVEL_ENV = "CHEMIO_LOGLEVEL"


def version():
    return __version__


def set_loglevel(loglevel):
    os.environ[LOGLEVEL_ENV] = str(loglevel)
    main.logger = modlog.getLogger(main.__name__)
