#!/usr/bin/python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

import requests

import logging
import argparse

import time

# ----------------------------------------------------------------------------------------
DEBUG = False

if DEBUG:
    network = '127.0.0.'
    logroot = './Logs/'
else:
    network = '172.17.0.'
    logroot = '/mnt/dat/'
# ----------------------------------------------------------------------------------------

def init_argparse():
    parser = argparse.ArgumentParser('Backend server node')
    parser.add_argument('discovery', type=str, default='0.0.0.0', help='Discovery URL')
    args = parser.parse_args()
    return args


def return_ip():
    import re, subprocess

    if DEBUG:
        ip = 'ip addr show lo'
    else:
        ip = 'ip addr show eth0'

    egrep = r'egrep (inet\W){1}'

    grep = subprocess.Popen(egrep.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    addr = subprocess.Popen(ip.split(), stdout=grep.stdin)
    output = grep.communicate()[0]
    x = re.compile(b'(\d+).(\d+).(\d+).(\d+)')
    res = x.search(output).group(0).decode()
    return res


def find_discovery():
    number = 2
    while True:
        ip = network + '{0}'.format(number)
        number += 1
        try:
            r = requests.get('http://'+ip+':8000/find')
            if r.status_code == 200:
                return ip
        except requests.ConnectionError:
            continue
    logging.warning("Backend -- found discovery")


def ip_checkin(node_ip, discovery):
    data = {1: node_ip}
    ok = False
    while not ok:
        try:
            req = requests.post('http://'+discovery+':8000/backend/checkin', data=data)
            ok = True
        except requests.RequestException:
            logging.critical('Unable to reach discovery node - auto-reconnect after 10 sec.')
            time.sleep(10)
    return


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200,'OK')
        self.send_header('content-type','text/html')
        self.end_headers()
        logging.warning('GET from {0}'.format(self.client_address))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

# -------------------------------------------------------------------------------------------


def is_exists(logname):
    import os
    try:
        os.stat(logname)
        return True
    except FileNotFoundError:
        return False


current_node_ip = return_ip()

num = 0
while True:
    if is_exists(logroot+'backend_{0}-launch{1}.log'.format(current_node_ip, num)):
        num += 1
        continue
    else:
        break

logpath = logroot+'backend_{0}-launch{1}.log'.format(current_node_ip, num)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.WARNING)

discoveryip = find_discovery()
ip_checkin(current_node_ip, discoveryip)

server = ThreadedHTTPServer(('0.0.0.0', 10000), HttpHandler)
server.serve_forever()
# serv = HTTPServer(('0.0.0.0', 10000), HttpHandler)
# serv.serve_forever()
