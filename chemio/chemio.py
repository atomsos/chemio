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

def select_server(servers=SERVER_URL):
    if isinstance(servers, str):
        servers = servers.strip().split()
    if len(servers) == 1:
        return servers[0]
    for server in servers:
        try:
            requests.get(server)
            return server
        except:
            pass
    raise ValueError("All servers are not available")


def get_response(iotype, filename, data=None, server=None):
    server = server or select_server()
    data = data or dict()
    data['iotype'] = iotype
    if iotype == 'read':
        files = {'file' : open(filename, 'rb')}
    else:
        files = None
    res = requests.post(server, files=files, data=data)
    # print(res.text, res.request.body)
    return res.text

def read(filename, index=-1, server=None):
    assert os.path.exists(filename)
    assert isinstance(index, int) or isinstance(index, str) and re.match('^[+-:0-9]$', index)
    extension = os.path.splitext(filename)[-1]
    if extension in compression:
        extension = os.path.splitext(os.path.splitext(filename)[0])[-1]
    extension = extension[1:]
    if not extension:
        extension = os.path.basename(filename)
    assert extension in SUPPORT_READ_EXTENSIONS, filename + ' not support'
    output = get_response('read', filename, {'index': index}, server=server)
    return json_tricks.loads(output)


def get_write_content(arrays, filename=None, format=None, server=None):
    data = dict()
    if filename:
        data['filename'] = filename
    else:
        assert format is not None, 'format cannot be none when filename is None'
        data['format'] =  format
    data.update({'arrays' : json_tricks.dumps(arrays)})
    return get_response('write', None, data=data, server=server)


def write(arrays, filename, format=None, server=None):
    output = get_write_content(arrays, filename=filename, format=format, server=server)
    with open(filename, 'w') as fd:
        fd.write(output)


def preview(arrays, format='xyz', server=None):
    output = get_write_content(arrays, format=format, server=server)
    print('----start----')
    print(re.findall('<body>([\s\S]*?)</body>', output)[0], end='')
    print('----end------')


