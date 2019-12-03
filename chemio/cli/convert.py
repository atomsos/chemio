"""


cli for convert


"""


import textwrap
from chemio.supported_writetypes import get_supported_writetypes
from . import utils


class CLICommand:
    """Convert between file formats.

    Use "-" for stdin/stdout.
    See "chemio info --formats" for known formats.
    """

    @staticmethod
    def add_arguments(parser):
        typeslines = '\033[31m' + '\n'.join(get_supported_writetypes()) + '\033[0m'
        add = parser.add_argument
        add('-v', '--verbose', action='store_true',
            help='Print names of converted files')
        add('input',  # nargs='+',
            metavar='input-file')
        add('-i', '--input-format', metavar='FORMAT',
            help='Specify input FORMAT')
        add('output', metavar='output-file')
        add('-o', '--output-format', metavar='FORMAT',
            help=typeslines)
        add('-f', '--force', action='store_true',
            help='Overwrite an existing file')
        add('--compresslevel', default=1, type=int,
            help='compression level, 0 to shutdown')
        add('-n', '--image-number',
            default=':', metavar='NUMBER',
            help='Pick images from trajectory.  NUMBER can be a '
            'single number (use a negative number to count from '
            'the back) or a range: start:stop:step, where the '
            '":step" part can be left out - default values are '
            '0:nimages:1.')
        add('--data', nargs='*',
            help='data to be posted, key=val format')
        add('--calc_data', nargs='*',
            help='calc data to be posted, key=val format')
        # add('-e', '--exec-code',
        #     help='Python code to execute on each atoms before '
        #     'writing it to output file. The Atoms object is '
        #     'available as `atoms`. Set `atoms.info["_output"] = False` '
        #     'to suppress output of this frame.')
        # add('-E', '--exec-file',
        #     help='Python source code file to execute on each '
        #     'frame, usage is as for -e/--exec-code.')
        # add('-a', '--arrays',
        #     help='Comma-separated list of atoms.arrays entries to include '
        #     'in output file. Default is all entries.')
        # add('-I', '--info',
        #     help='Comma-separated list of atoms.info entries to include '
        #     'in output file. Default is all entries.')
        add('-s', '--split-output', action='store_true',
            help='Write output frames to individual files. '
            'Output file name should be a format string with '
            'a single integer field, e.g. out-{:0>5}.xyz')

    @staticmethod
    def run(args, parser):
        import chemio
        if args.verbose:
            print(', '.join(args.input), '->', args.output)
        data = utils.parse_args_data(args.data)
        calc_data = utils.parse_args_data(args.calc_data)
        if args.debug:
            chemio.set_loglevel('debug')
        chemio.convert(args.input, args.output, args.image_number,
                       args.input_format, args.output_format,
                       data=data, calc_data=calc_data,
                       compresslevel=args.compresslevel,
                       )
