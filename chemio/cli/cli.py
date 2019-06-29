"""

chemio cli

"""


import argparse
import chemio



def run_chemio_cli():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("filename")
    parser.add_argument("-i", "--index", default=-1)
    parser.add_argument("-k", "--key")
    parser.add_argument("--type", nargs=1)
    args = parser.parse_args()
    arrays = chemio.read(filename=args.filename, index=args.index)
    if args.key:
        for key in args.key.split('/'):
            arrays = arrays[key]
        print(args.key, ':', arrays)
    else:
        print(arrays)


