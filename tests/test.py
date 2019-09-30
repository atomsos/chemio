"""


GSIO: IO using server



"""


import os
import random
import configparser
import logging
import tempfile

import argparse
import json_tricks
import ase.build
import chemio


chemio._setdebug()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


BASEDIR = os.path.dirname(os.path.abspath(__file__))
TESTDIR = os.path.join(BASEDIR, 'chem_file_samples/files')
BASEDIR = os.path.join(BASEDIR, '../chemio')
CONFIGFILE = os.path.join(BASEDIR, 'config.conf')

CONF = configparser.ConfigParser()
CONF.read(CONFIGFILE)
SUPPORT_READ_EXTENSIONS = CONF.get(
    "default", "support_read_extensions").strip().split()
SUPPORT_WRITE_FORMATS = CONF.get(
    "default", "support_write_formats").strip().split()


def test(args):
    if args.log:
        test_log()
    if args.ase:
        test_ase()
    if args.read:
        test_read()
    if args.write:
        test_write()


def check_write_correct(write_fname):
    with open(write_fname) as f:
        _str = f.read()
        if '500 Internal Server Error' in _str:
            raise RuntimeError('Internal Server Error')


def test_ase():
    # test ase
    arrays = ase.build.molecule("CH4")  # .arrays
    logger.debug("-"*50+'\n' + 'test ase:')
    for _format in SUPPORT_WRITE_FORMATS:
        logger.debug('-'*50+'\n'+_format)
        chemio.preview(arrays, _format)
        write_fname = f"{tempfile.mktemp()}_{_format}"
        logger.debug('-'*50+'\n'+write_fname)
        chemio.write(arrays, write_fname, _format)
        check_write_correct(write_fname)
        os.remove(write_fname)


def test_read():
    # test read
    logger.debug('-'*50+'\n'+'test read:')
    testfilenames = os.listdir(TESTDIR)
    random.shuffle(testfilenames)
    for filename in testfilenames[:10]:
        if filename.startswith('.'):
            continue
        logger.debug('-'*50+'\n'+filename)
        filename = os.path.join(TESTDIR, filename)
        if not os.path.isfile(filename):
            continue
        arrays = chemio.read(filename)
        arrays_string = json_tricks.dumps(arrays, allow_nan=True)
        logger.debug(f"{arrays_string[:1000]}")


def test_write():
    # test write
    arrays = ase.build.molecule("CH4")  # .arrays
    for _format in SUPPORT_WRITE_FORMATS:
        logger.debug('-'*50+'\n' + _format)
        chemio.preview(arrays, _format)
        write_fname = f"{tempfile.mktemp()}_{_format}"
        chemio.write(arrays, write_fname, _format)
        os.remove(write_fname)


def test_log():
    print("Lets test logging")
    logger.info("-"*50)
    logger.debug("-"*50)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", action="store_true")
    parser.add_argument("--ase", action="store_true")
    parser.add_argument("--read", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    test(args)
