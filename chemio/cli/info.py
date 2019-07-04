"""

chemio info cli 


"""
import json_tricks
import chemio


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
        parser.add_argument('filename', nargs='*',
                            help='Name of file to determine format for.')
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='Show more information about files.')
        parser.add_argument('-k', '--key',
                            help='key to show')

    @staticmethod
    def run(args):
        if not args.filename:
            raise ValueError("No filename is given")
        for filename in args.filename:
            arrays = chemio.read(filename)
            if args.verbose:
                print(arrays)
            if args.key:
                try:
                    print(filename, arrays[args.key])
                except:
                    print(filename, None)
            else:
                print(json_tricks.dumps(arrays, indent=4))
   
