"""

chemio info cli 


"""
import json_tricks
from . import utils
from atomtools.ext_types import ExtDict


class CLICommand:
    """Print information about files or system.

    Without any filename(s), informations about the Chemio installation will be
    shown (Python version, library versions, ...).

    With filename(s), the file format will be determined for each file.
    """

    @staticmethod
    def add_arguments(parser):
        add = parser.add_argument
        add('filename', nargs='*',
            help='Name of file to determine format for.')
        add('-i', '--index', default=-1,
            help='Index to show')
        add('-v', '--verbose', action='store_true',
            help='Show more information about files.')
        add('-k', '--key',
            help='key to show')
        add('--compresslevel', default=1, type=int,
            help='compression level, 0 to shutdown')
        add('-d', '--data', nargs='*',
            help='data to be posted, key=val format')
        add('--calc_data', nargs='*',
            help='calc data to be posted, key=val format')

    @staticmethod
    def run(args):
        if not args.filename:
            raise ValueError("No filename is given")
        data = utils.parse_args_data(args.data)
        calc_data = utils.parse_args_data(args.calc_data)
        import chemio
        if args.debug:
            chemio.set_loglevel('debug')
        for filename in args.filename:
            arrays = chemio.read(filename, index=args.index,
                                 compresslevel=args.compresslevel,
                                 data=data, calc_data=calc_data)
            if args.verbose:
                print(arrays)
            if args.key:
                print(filename)
                try:
                    print(ExtDict(arrays)[args.key])
                except:
                    print(None)
            else:
                print(json_tricks.dumps(arrays, allow_nan=True, indent=4))
