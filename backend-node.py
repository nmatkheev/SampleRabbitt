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


def ip_checkin(node_ip):
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

current_node_ip = '127.0.0.1'  # ---> you should get it via docker?

logpath = r'backend - {0}.log'.format(current_node_ip)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.INFO)

args = init_argparse()

discovery = args.discovery
ip_checkin(current_node_ip)

serv = HTTPServer(('0.0.0.0', 10000), HttpProcessor)
serv.serve_forever()
