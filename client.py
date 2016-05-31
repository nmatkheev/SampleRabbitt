#!/usr/bin/python3

import requests
import logging
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
    if DEBUG == True:
        return '127.0.0.1'

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
    logging.warning("Client -- found discovery")


def is_exists(logname):
    import os
    try:
        os.stat(logname)
        return True
    except FileNotFoundError:
        return False

time.sleep(3)
current_node_ip = return_ip()
discoveryip = find_discovery()

num = 0
while True:
    if is_exists(logroot+'client_{0}-launch{1}.log'.format(current_node_ip, num)):
        num += 1
        continue
    else:
        break

logpath = logroot+'client_{0}-launch{1}.log'.format(current_node_ip, num)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.WARNING)

front_nodes = None
back_nodes = None

while True:
    try:
        front_nodes = requests.get('http://' + discoveryip + ':8000/frontend').json()
        back_nodes = requests.get('http://' + discoveryip + ':8000/backend').json()
        break
    except requests.ConnectionError:
        continue

# for x in range(0,10):
while True:
    for key,value in front_nodes.items():
        try:
            r = requests.post('http://'+value+':9000', data=back_nodes)
            logging.warning("POST to Frontend - SUCCESS - Elapsed: {0} ".format(r.elapsed))
        except requests.ConnectionError:
            logging.warning("POST to Frontend - FAILED")
        time.sleep(2)