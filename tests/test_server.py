"""


GSIO: IO using server



"""



import os
import configparser
import chemio

BASEDIR = os.path.dirname(os.path.abspath(__file__))
TESTDIR = os.path.join(BASEDIR, 'Testcases')
BASEDIR = os.path.join(BASEDIR, '../chemio')
CONFIGFILE = os.path.join(BASEDIR, 'config.conf')

CONF = configparser.ConfigParser()
CONF.read(CONFIGFILE)
SUPPORT_READ_EXTENSIONS = CONF.get("default", "support_read_extensions").strip().split()
SUPPORT_WRITE_FORMATS = CONF.get("default", "support_write_formats").strip().split()
server = 'http://chemio.senrea.net/cgi-bin/chemio.py'
def test():
    for filename in os.listdir(TESTDIR):
        filename = os.path.join(TESTDIR, filename)
        if not os.path.isfile(filename):
            continue
        arrays = chemio.read(filename, server=server)
        print(arrays)
    for _format in SUPPORT_WRITE_FORMATS:
        print(_format)
        chemio.preview(arrays, _format,server=server)

if __name__ == '__main__':
    test()
