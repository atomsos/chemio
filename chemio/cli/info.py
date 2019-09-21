"""

chemio info cli 


"""
import json_tricks
import chemio
from . import utils


# from chemio.utils import import_module, FileNotFoundError
# from chemio.utils import search_current_git_hash
# from chemio.io.formats import filetype, all_formats, UnknownFileTypeError
# from chemio.io.ulm import print_ulm_info
# from chemio.io.bundletrajectory import print_bundletrajectory_info
# from chemio.io.formats import all_formats as fmts


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
        if args.debug:
            print(args)
            print(data, calc_data)
        for filename in args.filename:
            arrays = chemio.read(filename, index=args.index,
                                 format_nocheck=args.nocheck,
                                 data=data, calc_data=calc_data,
                                 debug=args.debug)
            if args.verbose:
                print(arrays)
            if args.key:
                try:
                    print(filename, arrays[args.key])
                except:
                    print(filename, None)
            else:
                print(json_tricks.dumps(arrays, indent=4))
