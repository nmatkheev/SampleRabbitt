#!/usr/bin/python3

from urllib import parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

import logging
import argparse

import time


def init_argparse():
    parser = argparse.ArgumentParser('Frontend server node')
    parser.add_argument('discovery', type=str, default='0.0.0.0', help='Discovery URL')
    args = parser.parse_args()
    return args


def ip_checkin(node_ip):
    data = {1: node_ip}
    ok = False
    while not ok:
        try:
            global discovery
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

        logging.info('Incoming POST from - {0}'.format(self.client_address))

        for key, value in post_data.items():
            try:
                req = requests.get('http://'+value[0]+':10000')
                logging.warning('Success GET - url: {0} - Elapsed: {1}, Status_code: {2}'.format(
                    'http://'+value[0]+':10000', req.elapsed, req.status_code
                ))
            except requests.ConnectionError:
                logging.critical('Failed GET - url: {0}'.format(
                    'http://'+value[0]+':10000'
                ))

        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200, 'OK')
        self.send_header('content-type', 'text/html')
        self.end_headers()

# ----------------------------------------------------------------------

current_node_ip = '127.0.0.1'  # ---> you should get it via docker?

args = init_argparse()
discovery = args.discovery

logpath = 'frontend - {0}.log'.format(current_node_ip)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.WARNING)

ip_checkin(current_node_ip)

serv = HTTPServer(('0.0.0.0', 9000), HttpHandler)
serv.serve_forever()
