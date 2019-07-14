"""


GSIO: IO using server



"""



import os
import random
import configparser
import ase.build 
import chemio



BASEDIR = os.path.dirname(os.path.abspath(__file__))
TESTDIR = os.path.join(BASEDIR, 'Testcases')
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
        chemio.preview(arrays, _format, debug=True)
        wfname = '/tmp/a.{0}'.format(_format)
        print('-'*50+'\n', wfname)
        chemio.write(wfname, arrays, _format, debug=True)
        os.remove(wfname)
    # test read
    testfilenames = os.listdir(TESTDIR)
    random.shuffle(testfilenames)
    for filename in testfilenames[:10]:
        filename = os.path.join(TESTDIR, filename)
        if not os.path.isfile(filename):
            continue
        arrays = chemio.read(filename, debug=True)
        print('-'*50+'\n', arrays)
    # test write
    for _format in SUPPORT_WRITE_FORMATS:
        print('-'*50+'\n', _format)
        chemio.preview(arrays, _format, debug=True)
        wfname = '/tmp/a.{0}'.format(_format)
        chemio.write(wfname, arrays, _format, debug=True)
        os.remove(wfname)

if __name__ == '__main__':
    test()
