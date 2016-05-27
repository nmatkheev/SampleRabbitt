#!/usr/bin/python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

import logging
import argparse

import time


def init_argparse():
    parser = argparse.ArgumentParser('Backend server node')
    parser.add_argument('discovery', type=str, default='0.0.0.0', help='Discovery URL')
    args = parser.parse_args()
    return args


def return_ip():
    import re, subprocess

    # ip = 'ip addr show eth0'
    ip = 'ip addr show lo'
    egrep = r'egrep (inet\W){1}'

    grep = subprocess.Popen(egrep.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    addr = subprocess.Popen(ip.split(), stdout=grep.stdin)
    output = grep.communicate()[0]
    x = re.compile(b'(\d+).(\d+).(\d+).(\d+)')
    res = x.search(output).group(0).decode()
    return res


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


class HttpProcessor(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200,'OK')
        self.send_header('content-type','text/html')
        self.end_headers()
        logging.warning('GET from {0}'.format(self.client_address))

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
    if is_exists('backend_{0}-launch{1}.log'.format(current_node_ip, num)):
        num += 1
        continue
    else:
        break

logpath = 'backend_{0}-launch{1}.log'.format(current_node_ip, num)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.WARNING)

args = init_argparse()

discoveryip = args.discovery
ip_checkin(current_node_ip, discoveryip)

serv = HTTPServer(('0.0.0.0', 10000), HttpProcessor)
serv.serve_forever()
