# CHEMIO


Chemical file IO




## read/write

```python
import chemio
chemio.read(filename, index)
chemio.write(arrays, filename, format)
```


## cli

```bash
# chemio -h
usage: chemio [-h] [-i INDEX] [-k KEY] [--type TYPE] filename

positional arguments:
  filename

optional arguments:
  -h, --help            show this help message and exit
  -i INDEX, --index INDEX
  -k KEY, --key KEY
  --type TYPE


chemio filename
```
