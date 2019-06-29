"""


GSIO: IO using server



"""



import os
import re
import configparser
import requests
import json_tricks
import atomtools



BASEDIR = os.path.dirname(os.path.abspath(__file__))
CONFIGFILE = os.path.join(BASEDIR, 'config.conf')

CONF = configparser.ConfigParser()
CONF.read(CONFIGFILE)
SERVER_URL = CONF.get("default", "server")
SUPPORT_READ_EXTENSIONS = CONF.get("default", "support_read_extensions").strip().split()
SUPPORT_WRITE_FORMATS = CONF.get("default", "support_write_formats").strip().split()
compression = atomtools.file.compress_command


def get_response(iotype, filename, data=None):
    data = data or dict()
    data['iotype'] = iotype
    if iotype == 'read':
        files = {'file' : open(filename, 'rb')}
    else:
        files = None
    res = requests.post(SERVER_URL, files=files, data=data)
    return res.text

def read(filename, index=-1):
    assert os.path.exists(filename)
    assert isinstance(index, int) or isinstance(index, str) and re.match('^[+-:0-9]$', index)
    extension = os.path.splitext(filename)[-1]
    if extension in compression:
        extension = os.path.splitext(os.path.splitext(filename)[0])[-1]
    extension = extension[1:]
    if not extension:
        extension = os.path.basename(filename)
    assert extension in SUPPORT_READ_EXTENSIONS, filename + ' not support'
    output = get_response('read', filename, {'index': index})
    return json_tricks.loads(output)


def get_write_content(arrays, filename=None, format=None):
    data = dict()
    if filename:
        data['filename'] = filename
    else:
        assert format is not None, 'format cannot be none when filename is None'
        data['format'] =  format
    data.update({'arrays' : json_tricks.dumps(arrays)})
    return get_response('write', None, data=data)


def write(arrays, filename, format=None):
    output = get_write_content(arrays, filename=filename, format=format)
    with open(filename, 'w') as fd:
        fd.write(output)


def preview(arrays, format='xyz'):
    output = get_write_content(arrays, format=format)
    print('----start----')
    print(re.findall('<body>([\s\S]*?)</body>', output)[0], end='')
    print('----end------')


def test():
    arrays = read('test.xyz')
    print(arrays)
    arrays = read('POSCAR')
    print(arrays)
    for _format in SUPPORT_WRITE_FORMATS:
        print(_format)
        preview(arrays, _format)

if __name__ == '__main__':
    test()
