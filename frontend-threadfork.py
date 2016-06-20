#!/usr/bin/python3

from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer

from socketserver import ThreadingMixIn

import requests

import logging
import argparse

import time

# ----------------------------------------------------------------------------------
DEBUG = False

if DEBUG:
    network = '127.0.0.'
    logroot = './Logs/'
else:
    network = '172.17.0.'
    logroot = '/mnt/dat/'
# ----------------------------------------------------------------------------------

def init_argparse():
    parser = argparse.ArgumentParser('Frontend server node')
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
    limit = 20
    number = 2
    while True:
        ip = network + '{0}'.format(number)
        number += 1
        if number == limit:  # bugfix
            number = 2
        try:
            r = requests.get('http://'+ip+':8000/find')
            if r.status_code == 200:
                return ip
        except requests.ConnectionError:
            continue
    logging.warning("Frontend -- found discovery")


def ip_checkin(node_ip, discovery):
    data = {1: node_ip}
    ok = False
    while not ok:
        try:
            req = requests.post('http://'+discovery+':8000/frontend/checkin', data=data)
            ok = True
        except requests.RequestException:
            logging.critical('Unable to reach discovery node - auto-reconnect after 10 sec.')
            time.sleep(10)
    return


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = parse.parse_qs(self.rfile.read(length).decode('utf-8'))

        logging.warning('Incoming POST {0}'.format(self.client_address))

        for key, value in post_data.items():
            try:
                req = requests.get('http://'+value[0]+':10000')
                logging.warning('Success GET ({0})   Elapsed: {1}   Status_code: {2}'.format(
                    'http://'+value[0]+':10000', req.elapsed, req.status_code
                ))
            except requests.ConnectionError:
                logging.critical('Failed GET ({0})'.format(
                    'http://'+value[0]+':10000'
                ))

        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200, 'OK')
        self.send_header('content-type', 'text/html')
        self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


# ----------------------------------------------------------------------


def is_exists(logname):
    import os
    try:
        os.stat(logname)
        return True
    except FileNotFoundError:
        return False


discoveryip = find_discovery()

current_node_ip = return_ip()
ip_checkin(current_node_ip, discoveryip)

num = 0
while True:
    if is_exists(logroot+'frontend_{0}-launch{1}.log'.format(current_node_ip, num)):
        num += 1
        continue
    else:
        break

logpath = logroot+'frontend_{0}-launch{1}.log'.format(current_node_ip, num)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.WARNING)


server = ThreadedHTTPServer(('0.0.0.0', 9000), HttpHandler)
server.serve_forever()
# serv = HTTPServer(('0.0.0.0', 9000), HttpHandler)
# serv.serve_forever()
