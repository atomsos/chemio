"""


GSIO: IO using server



"""


import os
import re
import urllib.parse
import configparser
import gzip
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json_tricks

import atomtools.fileutil
import atomtools.filetype
import atomtools.types


BASEDIR = os.path.dirname(os.path.abspath(__file__))
CONFIGFILE = os.path.join(BASEDIR, 'config.conf')

CONF = configparser.ConfigParser()
CONF.read(CONFIGFILE)
SUPPORT_READ_EXTENSIONS = CONF.get(
    "default", "support_read_extensions").strip().split()
SUPPORT_WRITE_FORMATS = CONF.get(
    "default", "support_write_formats").strip().split()


CHEMIO_SERVER_URLS = os.environ.get(
    "CHEMIO_SERVER_URLS", CONF.get("default", "server"))
USING_COMPRESSION = bool(os.environ.get("CHEMIO_USING_COMPRESSION", 'True'))


global SERVER
SERVER = None



def assemble_data(data):
    assert isinstance(data, dict)
    return ';'.join([f"{key}={val}" for key, val in data.items()])

def server_available(server):
    """
    test if a server is available
    Input:
        * server: str, a hostname/ip/url
    Output:
        * available: bool, True if server is available
    """
    netloc = urllib.parse.urlsplit(server).netloc.split(":")[0]
    if os.system('ping  -W 1 -c 1 {0} > /dev/null 2>&1 || \
                  ping6 -W 1 -c 1 {0} > /dev/null 2>&1'.format(netloc)) == 0:
        return server, True
    return server, False


def select_server(servers=CHEMIO_SERVER_URLS, debug=False):
    """
    give out a available server
    Input:
        * servers: list/str, list of servers in list or string format
        * debug: boolean
    Output:
        * the best server available
    """
    global SERVER
    executor = ThreadPoolExecutor(max_workers=10)
    if SERVER is not None:
        return SERVER
    if isinstance(servers, str):
        servers = servers.strip().split()
    if len(servers) == 1:
        return servers[0]
    all_tasks = []
    server_availability = OrderedDict()
    for server in servers:
        all_tasks.append(executor.submit(server_available, server))
        server_availability[server] = False
    for task in as_completed(all_tasks):
        server, available = task.result()
        server_availability[server] = available
    if debug:
        print(server_availability)
    for server in servers:
        if server_availability[server]:
            return server
    raise ValueError("All servers are not available")


def get_response(method, files=None, data=None, calc_data=None, debug=False):
    """
    get response from server
    Input:
        * method: string, read/write/convert
        * files: dict/None, list of files be uploaded
        * data: dict, dictionary to be transferred
        * debug: boolean, default False
    Output:
        * response from server as string
    """
    assert method in ['read', 'write', 'convert']
    import requests
    server = select_server(debug=debug)
    data = data or dict()
    url = server + '/' + method
    if server.endswith('/'):
        url = server + method
    data['method'] = method
    res = requests.post(url, files=files, data=data)
    if debug:
        print('\n\nheader:\n{0}'.format(res.headers))
        print('\n\ntext:\n{0}'.format(res.text))
    return res.text


def get_compressed_file(filename):
    """
    compress file before uploading
    Input:
        * filename: string, the file to be compressed
    Output:
        compressed_filename, True/False
    """
    if atomtools.fileutil.is_compressed_file(filename) or not USING_COMPRESSION:
        return filename, False
    compressed_filename = filename+'.gz'
    compressed_filename = os.path.join(
        '/tmp', os.path.basename(compressed_filename))
    with open(filename, 'rb') as f_in:
        with gzip.open(compressed_filename, 'wb', compresslevel=3) as f_out:
            f_out.write(f_in.read())
    return compressed_filename, True


def read(read_filename, index=-1, format=None, format_nocheck=False,
         data=None, calc_data=None, debug=False):
    assert os.path.exists(read_filename), '{0} not exist'.format(read_filename)
    assert isinstance(index, int) or isinstance(index, str) and \
        re.match('^[+-:0-9]$', index), '{0} is not a int or :'.format(index)
    if not format_nocheck:
        format = format or atomtools.filetype.filetype(read_filename)
    if format is None:
        raise NotImplementedError(
            'format cannot be parsed, please check filetype')
    compressed_filename, remove_flag = get_compressed_file(read_filename)
    files = {'read_file': open(compressed_filename, 'rb')}
    data = data or dict()
    data = assemble_data(data)
    calc_data = calc_data or dict()
    calc_data = assemble_data(calc_data)
    data = {'data': data, 
            'calc_data' : calc_data,
            'read_index': index,
            'read_format': format,
            'read_filename' : os.path.basename(read_filename)}
    output = get_response('read', files, data, debug=debug)
    if remove_flag:
        os.remove(compressed_filename)
    if debug:
        print(files, data, output)
    output = json_tricks.loads(output)
    if isinstance(output, dict):
        output = atomtools.types.ExtDict(output)
    elif isinstance(output, list):
        output = [atomtools.types.ExtDict(_) for _ in output]
    return output


def check_multiframe(arrays, format):
    assert format in atomtools.filetype.list_supported_formats(), \
        '{0} not in {1}'.format(
            format, atomtools.filetype.list_supported_formats())
    if isinstance(arrays, dict) or isinstance(arrays, list)\
            and atomtools.filetype.support_multiframe(format):
        return True
    return False


def get_write_content(arrays, format=None, data=None, calc_data=None, debug=False, **kwargs):
    assert format is not None, 'format cannot be none when filename is None'
    data = data or dict()
    data = assemble_data(data)
    calc_data = calc_data or dict()
    calc_data = assemble_data(calc_data)
    data = {'data': data, 
            'calc_data' : calc_data,
            'write_format': format}
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
            print(
                'format {0} not support list array, turns to last image'.format(format))
        arrays = arrays[-1]
    if debug:
        print(kwargs)
    arrays.update(kwargs)
    data = {'data': data, 'arrays': json_tricks.dumps(arrays)}
    output = get_response('write', None, data=data, calc_data=calc_data, debug=debug)
    return output


def write(write_filename, arrays, format=None, format_nocheck=False, data=None, calc_data=None, debug=False):
    if not format_nocheck:
        format = format or atomtools.filetype.filetype(write_filename)
        assert format is not None, 'We cannot determine your filetype. Supports {0}'.format(
            ' '.join(SUPPORT_WRITE_FORMATS))
        assert format in SUPPORT_WRITE_FORMATS, 'format {0} not writeable'.format(
            format)
    if write_filename == '-':
        preview(arrays, format=format, data=data, calc_data=calc_data, debug=debug)
    else:
        # arrays['write_filename'] = filename
        kwargs = {'write_filename': write_filename}
        output = get_write_content(
            arrays, format=format, data=data, calc_data=calc_data, debug=debug, **kwargs)
        with open(write_filename, 'w') as fd:
            fd.write(output)


def convert(read_filename, write_filename, index=-1,
            read_format=None, write_format=None,
            format_nocheck=False, data=None, calc_data=None, debug=False):
    assert os.path.exists(read_filename), '{0} not exist'.format(read_filename)
    if not format_nocheck:
        read_format = read_format or atomtools.filetype.filetype(read_filename)
        assert read_format is not None, \
            'We cannot determine your filetype of file: {0}'.format(
                read_filename)
    write_format = write_format or atomtools.filetype.filetype(write_filename)
    assert write_format is not None, \
        'We cannot determine your filetype of file: {0}'.format(write_filename)
    compressed_filename, remove_flag = get_compressed_file(read_filename)
    files = {'read_file': open(compressed_filename, 'rb')}
    data = data or dict()
    data = assemble_data(data)
    calc_data = calc_data or dict()
    calc_data = assemble_data(calc_data)
    data = {'data': data,
            'calc_data' : calc_data,
            'read_index': index,
            'read_format': read_format,
            'write_filename': write_filename,
            'write_format': write_format}
    output = get_response('convert', files, data, debug=debug)
    if remove_flag:
        os.remove(compressed_filename)
    if write_filename == '-':
        __preview__(output)
    else:
        with open(write_filename, 'w') as fd:
            fd.write(output)


def preview(arrays, format='xyz', data=None, calc_data=None, debug=False):
    output = get_write_content(arrays, format=format, data=data, calc_data=calc_data, debug=debug)
    __preview__(output)


def __preview__(output):
    print('----start----')
    print(output)
    print('----end------')
