"""


GSIO: IO using server



"""


import os
import re
import configparser
import gzip
from io import StringIO, BytesIO
import modlog
import json_tricks
import requests

import atomtools.fileutil
import atomtools.filetype
import atomtools.methods

logger = modlog.getLogger(__name__)

BASEDIR = os.path.dirname(os.path.abspath(__file__))
CONFIGFILE = os.path.join(BASEDIR, 'config.conf')

CONF = configparser.ConfigParser()
CONF.read(CONFIGFILE)
SUPPORT_READ_EXTENSIONS = CONF.get(
    "default", "support_read_extensions").strip().split()
SUPPORT_WRITE_FORMATS = CONF.get(
    "default", "support_write_formats").strip().split()
CHEMIO_SERVER_URL = os.environ.get(
    "CHEMIO_SERVER_URL", CONF.get("default", "server"))

logger.debug(f"CHEMIO_SERVER_URL: {CHEMIO_SERVER_URL}")


class ChemioReadError(Exception):
    pass


def read_ase(filename, index=None, format=None,
             parallel=True, **kwargs):
    """
    read ase type data
    """
    import ase.io
    return ase.io.read(filename, index=index, format=format,
                       parallel=parallel, **kwargs)


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


def base_convert(read_obj, read_index: int = -1, read_format=None,
                 write_filename=None, write_format=None,
                 data=None, calc_data=None,
                 compress: bool = True, compresslevel: int = 1,
                 ):
    """
    base convert: convert anything from one type to another
    Input:
        read_obj: filename/StringIO/Atoms/Structure like
        read_index: int, which frame to read
        read_format: format of object
        write_filename: used for generating output
        write_format: what type to write
        data: dict, extra data written to arrays
        calc_data: dict, extra data write to calc_arrays
        compress: whether to compress the file, default True
        compresslevel: int, level of compress
    Output:
        string: transformed structure from read_format to write_format
    """
    rawbytes, read_filename, compressed = parse_input_obj(read_obj)
    if compresslevel == 0:
        compress = False
    if not compressed and compress and len(rawbytes) > 8 * 1024:
        rawbytes = gzip.compress(rawbytes, compresslevel)
        compressed = True
    if read_filename is None:
        assert read_format is not None
        read_filename = f"{atomtools.name.randString()}.{read_format}"
    files = {
        'read_file': (read_filename, BytesIO(rawbytes)),
    }
    payload = {
        'read_index': read_index,
        'read_format': read_format,
        'write_format': write_format,
        'write_filename': write_filename,
        'compressed': compressed,
        'data': json_tricks.dumps(data, allow_nan=True),
        'calc_data': json_tricks.dumps(calc_data, allow_nan=True),
    }
    default_url = "https://io.autochemistry.com/convert"
    url = os.environ.get("CHEMIO_SERVER_URL", default_url)
    logger.debug(f"url: {url}, files: {files}, payload: {payload}")
    response = requests.post(url, files=files, data=payload)
    result = response.json()
    logger.debug(f"result: {result}")
    if result['success']:
        return result['data']
    raise ChemioReadError(result['message'])


def read(read_obj, index=-1, format=None,
         data=None, calc_data=None,
         compress: bool = True, compresslevel: int = 1,
         ):
    """
    Read read_obj with index and transform to arrays
    Input:
        read_obj: filename/StringIO
        index: index of the file if it contains multiple images.
        format: format of the file, if read_obj is StringIO cannot be None
        data: appended data for arrays
        calc_data: appended data for calc_arrays
    Output:
        dict: result of parsed read_obj
    """
    if isinstance(read_obj, str):
        fname_match = re.match('^(.*)@([0-9:+-]+)$', read_obj)
        if fname_match and os.path.isfile(fname_match.group[1]):
            read_obj, index = fname_match[1], fname_match[2]
    output = base_convert(read_obj, read_index=index, read_format=format,
                          write_format='json', data=data, calc_data=calc_data,
                          compress=compress, compresslevel=compresslevel,
                          )
    output = json_tricks.loads(output)
    return output


def check_multiframe(arrays, format):
    """
    check if multiple frame is supported
    """
    assert format in atomtools.filetype.list_supported_formats(), \
        '{0} not in {1}'.format(
            format, atomtools.filetype.list_supported_formats())
    if isinstance(arrays, dict) or isinstance(arrays, list)\
            and atomtools.filetype.support_multiframe(format):
        return True
    return False


def write(arrays, write_filename, format=None, index=-1,
          data=None, calc_data=None,
          compress: bool = True, compresslevel: int = 1,
          ):
    """
    write an array to specific format
    Input:
        arrays: dict/list, Atoms like dict
        write_filename: filename to write, None/- means to stdout
        format: None/str, format to write
        index: int, index of frame to write
        data/calc_data
        compress/compresslevel
    Output:
        None
    """
    output = base_convert(arrays, index, 'json', write_filename, format,
                          data=data, calc_data=calc_data,
                          compress=compress, compresslevel=compresslevel)
    if write_filename in [None, '-']:
        __preview_output__(output)
    else:
        with open(write_filename, 'w') as fd:
            fd.write(output)


def convert(read_obj, write_filename, index=-1,
            read_format=None, write_format=None,
            data=None, calc_data=None,
            compress: bool = True, compresslevel: int = 1,
            ):
    """
    convert any kind of structure related input
        (filename/filestring/Atoms/Structure) to any other kind
    Input:
        read_obj: filename/StringIO/Atoms/Structure
        write_filename: filename/None
        index: index of the frame of read_obj
        read_format: format of read_obj
        write_format: format of write_obj
        data: dict, extra data to be posted as arrays
        calc_data: dict, extra data to be posted as calc_arrays
    Output:
        None
    """
    output = base_convert(read_obj, index, read_format,
                          write_filename, write_format,
                          data=data, calc_data=calc_data,
                          compress=compress, compresslevel=compresslevel)
    if write_filename in [None, '-']:
        __preview_output__(output)
    with open(write_filename, 'w') as fd:
        fd.write(output)


def preview(arrays, format='xyz', data=None, calc_data=None):
    """
    preview
    """
    write(arrays, None, format, data, calc_data)


def __preview_output__(output):
    """
    preview output
    """
    print('-'*10 + ' chemio preview start' + '-'*10)
    print(output)
    print('-'*10 + ' chemio preview end  ' + '-'*10)
