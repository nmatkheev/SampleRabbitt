#!/usr/bin/python3

from urllib import parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = parse.parse_qs(self.rfile.read(length).decode('utf-8'))

        if 'frontend/checkin' in self.path:
            for value in post_data.items():
                global frontbase
                frontbase[len(frontbase)] = value[1][0]
                print('Frontend base: ', frontbase)

                self.send_response(200)
                self.end_headers()
                return
        if 'backend/checkin' in self.path:
            for value in post_data.items():
                global backbase
                backbase[len(backbase)] = value[1][0]
                print('Backend base: ', backbase)

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

        if 'backend' in self.path:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            global backbase
            self.wfile.write(bytes(json.dumps(backbase), encoding='utf-8'))
            return


url = '0.0.0.0'
port = 8000
frontbase = {}
backbase = {}

serv = HTTPServer((url, port), HttpHandler)
serv.serve_forever()

