"""


GSIO: IO using server



"""


import os
import configparser
import modlog
import json_tricks
import requests

logger = modlog.getLogger(__name__)

BASEDIR = os.path.dirname(os.path.abspath(__file__))
CONFIGFILE = os.path.join(BASEDIR, 'config.conf')

CONF = configparser.ConfigParser()
CONF.read(CONFIGFILE)
CHEMIO_SERVER_URL = os.environ.get(
    "CHEMIO_SERVER_URL", CONF.get("default", "server"))

logger.debug(f"CHEMIO_SERVER_URL: {CHEMIO_SERVER_URL}")


class ChemioReadError(Exception):
    pass


def get_molecule(name: str, searchtype: str = 'formula'):
    """
    base convert: convert anything from one type to another
    Input:
        name: name of molecule, in formula or name
        searchtype: name/formula
    Output:
        string: transformed structure from read_format to write_format
    """
    default_url = "https://io.autochemistry.com/get_molecule"
    url = os.environ.get("CHEMIO_SERVER_URL", default_url)
    payload = {
        'id': name,
        'type': searchtype
    }
    logger.debug(f"url: {url}, payload: {payload}")
    response = requests.post(url, data=payload)
    result = json_tricks.loads(response.text)
    logger.debug(f"result: {result}")
    if result['success']:
        return result['data']
    raise ChemioReadError(result['message'])
