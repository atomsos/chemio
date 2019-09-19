"""


GSIO: IO using server



"""



import os
import random
import configparser
import json_tricks
import ase.build 
import chemio



BASEDIR = os.path.dirname(os.path.abspath(__file__))
TESTDIR = os.path.join(BASEDIR, 'chem_file_samples/files')
BASEDIR = os.path.join(BASEDIR, '../chemio')
CONFIGFILE = os.path.join(BASEDIR, 'config.conf')

CONF = configparser.ConfigParser()
CONF.read(CONFIGFILE)
SUPPORT_READ_EXTENSIONS = CONF.get("default", "support_read_extensions").strip().split()
SUPPORT_WRITE_FORMATS = CONF.get("default", "support_write_formats").strip().split()

def test():
    # test ase
    arrays = ase.build.molecule("CH4") # .arrays
    for _format in SUPPORT_WRITE_FORMATS:
        print('-'*50+'\n', _format)
        chemio.preview(arrays, _format, debug=False)
        wfname = '/tmp/a.{0}'.format(_format)
        print('-'*50+'\n', wfname)
        chemio.write(wfname, arrays, _format, debug=False)
        os.remove(wfname)
    # test read
    testfilenames = os.listdir(TESTDIR)
    random.shuffle(testfilenames)
    for filename in testfilenames[:10]:
        if filename.startswith('.'):
            continue
        print('-'*50+'\n', filename)
        filename = os.path.join(TESTDIR, filename)
        if not os.path.isfile(filename):
            continue
        arrays = chemio.read(filename, debug=False)
        print(json_tricks.dumps(arrays)[:1000])
    # test write
    for _format in SUPPORT_WRITE_FORMATS:
        print('-'*50+'\n', _format)
        chemio.preview(arrays, _format, debug=False)
        wfname = '/tmp/a.{0}'.format(_format)
        chemio.write(wfname, arrays, _format, debug=True)
        os.remove(wfname)

if __name__ == '__main__':
    test()
