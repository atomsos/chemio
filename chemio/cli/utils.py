"""



args utils are stored here.


"""



import re




def parse_args_data(args):
    data = dict()
    if args.data:
        for d in args.data:
            match = re.match('^(.*?)=(.*)$', d)
            if match:
                key, val = match[1], match[2]
                data[key] = val
            else:
                raise ValueError("args data: d not a=b format")







