#!/usr/bin/python3

from urllib import parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

import logging
import json

# ----------------------------------------------------------------------------------
DEBUG = False

if DEBUG:
    network = '127.0.0.'
    logroot = './'
else:
    network = '172.17.0.'
    logroot = '/mnt/dat/'
# ----------------------------------------------------------------------------------

def is_exists(logname):
    import os
    try:
        os.stat(logname)
        return True
    except FileNotFoundError:
        return False


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


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = parse.parse_qs(self.rfile.read(length).decode('utf-8'))

        if 'frontend/checkin' in self.path:
            for key, value in post_data.items():
                global frontbase
                for x, y in frontbase.items():
                    if y == value[0]:
                        print("This node is already checked-in")
                        logging.warning("Frontend {0} -- Already checked-in".format(self.client_address))
                        self.send_response(200)
                        self.end_headers()
                        return
                logging.warning("Frontend {0} -- NOW checked-in".format(self.client_address))
                frontbase[len(frontbase)] = value[0]
                # print('Frontend base: ', frontbase)

                logging.warning("Current frontend list: {0}".format(frontbase))

                self.send_response(200)
                self.end_headers()
                return
        if 'backend/checkin' in self.path:
            for key, value in post_data.items():
                global backbase
                for x, y in backbase.items():
                    if y == value[0]:
                        logging.warning("Backend {0} -- Already checked-in".format(self.client_address))
                        self.send_response(200)
                        self.end_headers()
                        return
                logging.warning("Backend {0} -- NOW checked-in".format(self.client_address))
                backbase[len(backbase)] = value[0]
                print('Backend base: ', backbase)

                logging.warning("Current backend list: {0}".format(backbase))

                self.send_response(200)
                self.end_headers()
                return
        else:
            self.send_response(404)
            self.end_headers()
            return

    def do_GET(self):
        if 'frontend' in self.path:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            global frontbase
            self.wfile.write(bytes(json.dumps(frontbase), encoding='utf-8'))
            return
        elif 'backend' in self.path:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            global backbase
            self.wfile.write(bytes(json.dumps(backbase), encoding='utf-8'))
            return
        elif 'find' in self.path:
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
# ---------------------------------------------------------------------------------------------------

current_node_ip = return_ip()
num = 0
while True:
    if is_exists(logroot+'discovery_{0}-launch{1}.log'.format(current_node_ip, num)):
        num += 1
        continue
    else:
        break

logpath = logroot+'discovery_{0}-launch{1}.log'.format(current_node_ip, num)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.WARNING)


frontbase = {}
backbase = {}

server = ThreadedHTTPServer(('0.0.0.0', 8000), HttpHandler)
server.serve_forever()

# serv = HTTPServer((url, port), HttpHandler)
# serv.serve_forever()

