import os


BASEDIR = os.path.dirname(os.path.abspath(__file__))


def get_supported_writetypes():
    supported_writetypes = open(os.path.join(
        BASEDIR, 'supported_writetypes.txt')).read().split('\n')
    return supported_writetypes
