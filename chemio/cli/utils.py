"""



args utils are stored here.


"""



import re




def parse_args_data(args_data):
    data = dict()
    if args_data:
        for d in args_data:
            match = re.match('^(.*?)=(.*)$', d)
            if match:
                key, val = match[1], match[2]
                data[key] = val
            else:
                raise ValueError("args data: d not a=b format")

    return data






