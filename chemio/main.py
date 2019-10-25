"""


GSIO: IO using server



"""


import os
import re
import configparser
import gzip
import logging
from io import StringIO, BytesIO
import json_tricks
import requests

import atomtools.fileutil
import atomtools.filetype
import atomtools.methods

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

logger.debug(f"CHEMIO_SERVER_URLS: {CHEMIO_SERVER_URLS}")
global SERVER
SERVER = CHEMIO_SERVER_URLS


def assemble_data(arrays):
    return json_tricks.dumps(arrays, allow_nan=True)


def get_response(files=None, request_data=None):
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
    method = 'convert'
    server = CHEMIO_SERVER_URLS
    logger.debug(f"server: {CHEMIO_SERVER_URLS}")
    request_data = request_data or dict()
    if server.endswith('/'):
        url = server + method
    else:
        url = server + '/' + method
    res = requests.post(url, files=files, data=request_data)
    logger.debug(f"request_data: {request_data}")
    logger.debug(f'header: {res.headers}')
    logger.debug(f'text: {res.text}')
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


def read_ase(filename, index=None, format=None,
             parallel=True, **kwargs):
    import ase.io
    return ase.io.read(filename, index=index, format=format,
                       parallel=parallel, **kwargs)


def read(read_obj, index=-1, format=None, format_nocheck=False,
         data=None, calc_data=None):
    """
    Read read_obj with index and transform to arrays
    Input:
        read_obj:
            filename/StringIO
        index:
            index of the file if it contains multiple images.
        format:
            format of the file, if read_obj is StringIO cannot be None
        data:
            appended data for arrays
        calc_data:
            appended data for calc_arrays
    """
    fname_match = re.match('^(.*)@([0-9:+-]+)$', read_obj)
    if fname_match:
        read_obj, index = fname_match[1], fname_match[2]
    assert os.path.exists(read_obj), '{0} not exist'.format(read_obj)
    assert isinstance(index, int) or \
        isinstance(index, str) and \
        re.match('^[+-:0-9]$', index), '{0} is not a int or :'.format(index)
    if not format_nocheck:
        format = format or atomtools.filetype.filetype(read_obj)
    if format is None:
        raise NotImplementedError(
            'format cannot be parsed, please check filetype')
    compressed_filename, remove_flag = get_compressed_file(read_obj)
    files = {'read_file': open(compressed_filename, 'rb')}
    data = data or dict()
    data = assemble_data(data)
    calc_data = calc_data or dict()
    calc_data = assemble_data(calc_data)
    request_data = {
        'data': data,
        'calc_data': calc_data,
        'read_index': index,
        'read_format': format,
        'read_obj': os.path.basename(read_obj),
        'write_format': 'json',
    }
    output = get_response(files, request_data)
    if remove_flag:
        os.remove(compressed_filename)
    logger.debug(f"{files}, {data}, {output}")
    output = json_tricks.loads(output)
    return output


def check_multiframe(arrays, format):
    assert format in atomtools.filetype.list_supported_formats(), \
        '{0} not in {1}'.format(
            format, atomtools.filetype.list_supported_formats())
    if isinstance(arrays, dict) or isinstance(arrays, list)\
            and atomtools.filetype.support_multiframe(format):
        return True
    return False


def get_write_content(arrays, write_filename=None, format=None, data=None, calc_data=None):
    from io import StringIO
    assert format is not None, 'format cannot be none when filename is None'
    data = data or dict()
    data = assemble_data(data)
    calc_data = calc_data or dict()
    calc_data = assemble_data(calc_data)
    request_data = {
        'read_format': 'json',
        'data': data,
        'calc_data': calc_data,
        'write_filename': write_filename,
        'write_format': format,
    }
    files = {'read_file': StringIO(json_tricks.dumps(arrays, allow_nan=True))}
    output = get_response(files=files, request_data=request_data)
    return output


def write(arrays, write_filename=None, format=None,
          format_nocheck=False, data=None, calc_data=None):
    if not format_nocheck:
        format = format or atomtools.filetype.filetype(write_filename)
        assert format is not None, f'We cannot determine your filetype. Supports {SUPPORT_WRITE_FORMATS}'
        assert format in SUPPORT_WRITE_FORMATS, f'format {format} not writeable'
    if write_filename in [None, '-']:
        preview(arrays, format=format, data=data,
                calc_data=calc_data)
    else:
        output = get_write_content(
            arrays, write_filename=write_filename, format=format,
            data=data, calc_data=calc_data)
        with open(write_filename, 'w') as fd:
            fd.write(output)


def convert(read_obj, write_filename, index=-1,
            read_format=None, write_format=None,
            format_nocheck=False, data=None, calc_data=None):
    """
    convert any kind of structure related input(filename/filestring/Atoms/Structure) to any other kind
    Input:
        read_obj: filename/StringIO/Atoms/Structure
        read_format: 
    """
    assert os.path.exists(read_obj), '{0} not exist'.format(read_obj)
    # if not format_nocheck:
    #     read_format = read_format or atomtools.filetype.filetype(read_obj)
    #     assert read_format is not None, \
    #         'We cannot determine your filetype of file: {0}'.format(read_obj)
    write_format = write_format or atomtools.filetype.filetype(write_filename)
    assert write_format is not None, \
        'We cannot determine your filetype of file: {0}'.format(write_filename)
    compressed_filename, remove_flag = get_compressed_file(read_obj)
    files = {'read_file': open(compressed_filename, 'rb')}
    data = data or dict()
    data = assemble_data(data)
    calc_data = calc_data or dict()
    calc_data = assemble_data(calc_data)
    request_data = {
        'read_index': index,
        'read_format': read_format,
        'write_filename': write_filename,
        'write_format': write_format,
        'data': data,
        'calc_data': calc_data,
    }
    output = get_response(files=files, request_data=request_data)
    if remove_flag:
        os.remove(compressed_filename)
    if write_filename == '-':
        __preview__(output)
    else:
        with open(write_filename, 'w') as fd:
            fd.write(output)


def preview(arrays, format='xyz', data=None, calc_data=None):
    output = get_write_content(
        arrays, format=format, data=data, calc_data=calc_data)
    __preview__(output)


def __preview__(output):
    logger.critical('----start----')
    print(output)
    logger.critical('----end------')


def _setdebug():
    logger.setLevel(logging.DEBUG)


def parse_input_obj(inputobj):
    """
    parse inputobj to a bytes object
    Input:
        inputobj: filename/filestring/StringIO/BytesIO/Atoms/Structure
    Output:
        raw(bytes), filename(str), compressed(bool)
    """
    filename = None
    compressed = False
    if isinstance(inputobj, str):
        if os.path.exists(inputobj):
            filename = os.path.basename(inputobj)
            compressed = filename.endswith('.gz')
            if compressed:
                filename = filename[:-len('.gz')]
            return open(inputobj, 'rb').read(), filename, compressed
        else:
            return inputobj.encode(), filename, compressed
    elif isinstance(inputobj, bytes):
        return inputobj, filename, compressed
    elif isinstance(inputobj, (StringIO, BytesIO)):
        raw = inputobj.read()
        if isinstance(raw, str):
            raw = raw.encode()
        return raw, filename, compressed
    else:
        arrays = atomtools.methods.get_atoms_arrays(inputobj)
        filename = 'Atoms.json'
        return json_tricks.dumps(arrays, allow_nan=True).encode(), filename, compressed


class ChemioReadError(Exception):
    pass


def base_convert(read_obj, read_index: int = -1, read_format=None,
                 write_filename=None, write_format=None,
                 compress: bool = True, compresslevel: int = 1,
                 data=None, calc_data=None):
    """
    base convert: convert anything from one type to another
    Input:
        read_obj: filename/StringIO/Atoms/Structure like
        read_index: int, which frame to read
        read_format: format of object
        write_filename: used for generating output
        write_format: what type to write
        compress: if compress the file, default True, but force to False if the file has been compress
        compresslevel: int, level of compression
        data: dict, extra data written to arrays
        calc_data: dict, extra data write to calc_arrays
    Output:
        string: transformed structure from read_format to write_format
    """
    import pdb; pdb.set_trace()
    rawbytes, read_filename, compressed = parse_input_obj(read_obj)
    if not compressed and compress and len(rawbytes) > 8 * 1024:
        rawbytes = gzip.compress(rawbytes, compresslevel)
        compressed = True
    if read_filename is None:
        assert read_format is not None
    files = {
        'read_file': (read_filename, BytesIO(rawbytes)),
    }
    data = data or dict()
    calc_data = calc_data or dict()
    payload = {
        'read_index': read_index,
        'read_format': read_format,
        'write_format': write_format,
        'write_filename': write_filename,
        'compressed': compressed,
        'data': json_tricks.dumps(data, allow_nan=True),
        'calc_data': json_tricks.dumps(calc_data, allow_nan=True),
    }
    url = os.environ.get("CHEMIO_SERVER_URLS", "https://io.autochemistry.com")
    if not url.endswith('/'):
        url += '/'
    url += 'convert'
    response = requests.post(url, files=files, data=payload, timeout=2)
    result = response.json()
    if result['success']:
        return result['data']
    raise ChemioReadError(result['message'])
