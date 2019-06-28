"""


GSIO: IO using server



"""



import os
import configparser
import requests

BASEDIR = os.path.dirname(os.path.abspath(__file__))
CONFIGFILE = os.path.join(BASEDIR, 'config.conf')


global SERVER_URL
def get_server():
    global SERVER_URL
    conf = configparser.ConfigParser()
    conf.read(CONFIGFILE)
    SERVER_URL = conf.get("default", "server")


def read(filename, index=-1):
    global SERVER_URL
    requests.post(SERVER_URL, 



def write(arrays, filename, format='xyz'):
    global SERVER_URL
    requests.post(SERVER_URL, 
