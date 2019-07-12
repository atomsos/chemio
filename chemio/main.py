"""


GSIO: IO using server



"""



import os
import re
import urllib.parse
import configparser

import json_tricks
import atomtools



BASEDIR = os.path.dirname(os.path.abspath(__file__))
CONFIGFILE = os.path.join(BASEDIR, 'config.conf')

CONF = configparser.ConfigParser()
CONF.read(CONFIGFILE)
SUPPORT_READ_EXTENSIONS = CONF.get("default", "support_read_extensions").strip().split()
SUPPORT_WRITE_FORMATS = CONF.get("default", "support_write_formats").strip().split()


if os.environ.get("SERVER_URLS", None):
    SERVER_URLS = os.environ.get("SERVER_URLS")
else:
    SERVER_URLS = CONF.get("default", "server")
    COMPRESSION = atomtools.file.compress_command


global SERVER
SERVER = None



def select_server(servers=SERVER_URLS, debug=False):
    global SERVER
    if SERVER is not None:
        return SERVER
    if isinstance(servers, str):
        servers = servers.strip().split()
    if len(servers) == 1:
        return servers[0]
    for server in servers:
        netloc = urllib.parse.urlsplit(server).netloc.split(":")[0]
        if os.system('ping  -W 1 -c 1 {0} > /dev/null'.format(netloc)) == 0 or\
           os.system('ping6 -W 1 -c 1 {0} > /dev/null'.format(netloc)) == 0:
            SERVER = server
            if debug:
                print('server:', server)
            return server
    raise ValueError("All servers are not available")


def get_response(iotype, filename, data=None, debug=False):
    import requests
    server = select_server(debug=debug)
    data = data or dict()
    data['iotype'] = iotype
    if iotype == 'read':
        files = {'file' : open(filename, 'rb')}
    else:
        files = None
    if server.endswith('/'):
        url = server + iotype
    else:
        url = server + '/' + iotype
    res = requests.post(url, files=files, data=data)
    if debug:
        print(res.headers, res.text)
    return res.text


def read(filename, index=-1, format=None, debug=False):
    assert os.path.exists(filename)
    assert isinstance(index, int) or isinstance(index, str) and re.match('^[+-:0-9]$', index)
    format = format or atomtools.filetype(filename)
    if format is None:
        raise NotImplementedError('format cannot be parsed, please check filetype')
    output = get_response('read', filename, {'index': index, 'format' : format}, debug=debug)
    if debug:
        print(output)
    output = json_tricks.loads(output)
    if isinstance(output, dict):
        output = atomtools.types.ExtDict(output)
    elif isinstance(output, list):
        output = [atomtools.types.ExtDict(_) for _ in output]
    return output


def check_multiframe(arrays, format):
    assert format in atomtools.list_supported_formats()
    if isinstance(arrays, dict) or isinstance(arrays, list)\
        and atomtools.support_multiframe(format):
        return True
    return False


def get_write_content(arrays, format=None, debug=False):
    data = dict()
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
    if not check_multiframe(arrays, format):
        if debug:
            print('format {0} not support list array, turns to last image'.format(format))
        arrays = arrays[-1]
    data.update({'arrays' : json_tricks.dumps(arrays)})
    output = get_response('write', None, data=data, debug=debug)
    return output


def write(filename, arrays, format=None, debug=False):
    format = format or atomtools.filetype(filename)
    assert format is not None, 'We cannot determine your filetype supports {0}'.format(\
        ' '.join(SUPPORT_WRITE_FORMATS))
    assert format in SUPPORT_WRITE_FORMATS, 'format {0} not writeable'.format(format)
    if filename == '-':
        preview(arrays, format=format, debug=debug)
    else:
        arrays['filename'] = filename
        output = get_write_content(arrays, format=format, debug=debug)
        with open(filename, 'w') as fd:
            fd.write(output)


def preview(arrays, format='xyz', debug=False):
    output = get_write_content(arrays, format=format, debug=debug)
    print('----start----')
    print(output)
    print('----end------')

