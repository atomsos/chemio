"""


GSIO: IO using server



"""



import os
import re
import numpy
import configparser
import urllib
import requests
import json_tricks
import atomtools



BASEDIR = os.path.dirname(os.path.abspath(__file__))
CONFIGFILE = os.path.join(BASEDIR, 'config.conf')

CONF = configparser.ConfigParser()
CONF.read(CONFIGFILE)
SERVER_URLS = CONF.get("default", "server")
SUPPORT_READ_EXTENSIONS = CONF.get("default", "support_read_extensions").strip().split()
SUPPORT_WRITE_FORMATS = CONF.get("default", "support_write_formats").strip().split()
COMPRESSION = atomtools.file.compress_command

global SERVER
SERVER = None


def select_server(servers=SERVER_URLS):
    global SERVER
    if SERVER is not None:
        return SERVER
    if isinstance(servers, str):
        servers = servers.strip().split()
    if len(servers) == 1:
        return servers[0]
    for server in servers:
        netloc = urllib.parse.urlsplit(server).netloc
        if os.system('ping -W 1 -c 1 {0} > /dev/null'.format(netloc)) == 0:
            SERVER = server
            return server
    raise ValueError("All servers are not available")


def get_response(iotype, filename, data=None):
    server = select_server()
    data = data or dict()
    data['iotype'] = iotype
    if iotype == 'read':
        files = {'file' : open(filename, 'rb')}
    else:
        files = None
    res = requests.post(server, files=files, data=data)
    return res.text


def read(filename, index=-1, format=None):
    assert os.path.exists(filename)
    assert isinstance(index, int) or isinstance(index, str) and re.match('^[+-:0-9]$', index)
    extension = os.path.splitext(filename)[-1]
    if extension in COMPRESSION:
        extension = os.path.splitext(os.path.splitext(filename)[0])[-1]
    extension = extension[1:]
    if not extension:
        extension = os.path.basename(filename)
    assert extension in SUPPORT_READ_EXTENSIONS, filename + ' not support'
    # import pdb; pdb.set_trace()
    output = get_response('read', filename, {'index': index})
    output = json_tricks.loads(output)
    if isinstance(output, dict):
        output = atomtools.types.ExtDict(output)
    elif isinstance(output, list):
        output = [atomtools.types.ExtDict(_) for _ in output]
    return output


def get_write_content(arrays, filename=None, format=None):
    data = dict()
    if filename:
        data['filename'] = filename
    else:
        assert format is not None, 'format cannot be none when filename is None'
        data['format'] = format
    if arrays.__class__.__module__ == 'ase.atoms':
        calc_arrays = None
        if arrays.calc:
            calc_arrays = arrays.calc.parameters
            calc_arrays.update(arrays.calc.results)
        arrays = arrays.arrays
        if calc_arrays:
            arrays['calc_arrays'] = calc_arrays
    data.update({'arrays' : json_tricks.dumps(arrays)})
    return get_response('write', None, data=data)


def write(filename, arrays, format=None):
    if filename == '-':
        preview(arrays, format)
    else:
        output = get_write_content(arrays, filename=filename, format=format)
        with open(filename, 'w') as fd:
            fd.write(output)


def preview(arrays, format='xyz'):
    output = get_write_content(arrays, format=format)
    print('----start----')
    print(re.findall(r'<body>([\s\S]*?)</body>', output)[0], end='')
    print('----end------')


