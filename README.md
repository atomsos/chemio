# CHEMIO


Chemical file IO


[![Build Status](https://travis-ci.org/atomse/chemio.svg?branch=master)](https://travis-ci.org/atomse/chemio)
[![PyPI](https://img.shields.io/pypi/v/chemio.svg)](https://pypi.org/project/chemio)


## read/write

```python
import chemio
chemio.read(filename, index)
chemio.write(filename, arrays, format)
chemio.preview(arrays, format)
```


## cli

```bash
# chemio -h
usage: chemio [-h] [--version] [-T] {help,info,convert} ...

Chem IO command line tool.

optional arguments:
  -h, --help           show this help message and exit
  --version            show program's version number and exit
  -T, --traceback

Sub-commands:
  {help,info,convert}
    help               Help for sub-command.
    info               Print information about files or system.
    convert            Convert between file formats.
```



```bash
usage: chemio info [-h] [-v] [-k KEY] [filename [filename ...]]

Print information about files or system.

With filename(s), the file format will be determined for each file.

positional arguments:
  filename           Name of file to determine format for.

optional arguments:
  -h, --help         show this help message and exit
  -v, --verbose      Show more information about files.
  -k KEY, --key KEY  key to show

```



```bash
usage: chemio convert [-h] [-v] [-i FORMAT] [-o FORMAT] [-f] [-n NUMBER] [-s]
                      input-file [input-file ...] output-file

Convert between file formats.

Use "-" for stdin/stdout. See "chemio info --formats" for known formats.

positional arguments:
  input-file
  output-file

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Print names of converted files
  -i FORMAT, --input-format FORMAT
                        Specify input FORMAT
  -o FORMAT, --output-format FORMAT
                        Specify output FORMAT
  -f, --force           Overwrite an existing file
  -n NUMBER, --image-number NUMBER
                        Pick images from trajectory. NUMBER can be a single
                        number (use a negative number to count from the back)
                        or a range: start:stop:step, where the ":step" part
                        can be left out - default values are 0:nimages:1.
  -s, --split-output    Write output frames to individual files. Output file
                        name should be a format string with a single integer
                        field, e.g. out-{:0>5}.xyz
```
