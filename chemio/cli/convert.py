"""


cli for convert


"""


from . import utils


class CLICommand:
    """Convert between file formats.

    Use "-" for stdin/stdout.
    See "chemio info --formats" for known formats.
    """

    @staticmethod
    def add_arguments(parser):
        add = parser.add_argument
        add('-v', '--verbose', action='store_true',
            help='Print names of converted files')
        add('input',  # nargs='+',
            metavar='input-file')
        add('-i', '--input-format', metavar='FORMAT',
            help='Specify input FORMAT')
        add('output', metavar='output-file')
        add('-o', '--output-format', metavar='FORMAT',
            help='Specify output FORMAT')
        add('-f', '--force', action='store_true',
            help='Overwrite an existing file')
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
        if args.verbose:
            print(', '.join(args.input), '->', args.output)
        configs = []
        data = utils.parse_args_data(args.data)
        calc_data = utils.parse_args_data(args.calc_data)
        import chemio
        import logging
        if args.debug:
            chemio.main.logger.setLevel(logging.DEBUG)
        chemio.convert(args.input, args.output, args.image_number,
                       args.input_format, args.output_format,
                       format_nocheck=args.nocheck,
                       data=data, calc_data=calc_data)
