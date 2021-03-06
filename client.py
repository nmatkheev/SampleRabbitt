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
    limit = 20  # kostyl
    while True:
        ip = network + '{0}'.format(number)
        number += 1
        if number == limit:  # bugfix
            number = 2
        try:
            r = requests.get('http://'+ip+':8000/find')
            if r.status_code == 200:
                logging.warning("Client -- found discovery %s", ip)
                return ip
        except requests.ConnectionError:
            continue


def is_exists(logname):
    import os
    try:
        os.stat(logname)
        return True
    except FileNotFoundError:
        return False

logpath = logroot+'client.log'
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.WARNING)


# time.sleep(3)
current_node_ip = return_ip()
discoveryip = find_discovery()

num = 0
while True:
    if is_exists(logroot+'client_{0}-launch{1}.log'.format(current_node_ip, num)):
        num += 1
        continue
    else:
        break

# logpath = logroot+'client_{0}-launch{1}.log'.format(current_node_ip, num)
# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.WARNING)
# logging.debug("found discovery - %(ip)s", ip=discoveryip)


def query_discovery():
    while True:
        try:
            logging.warning("Entered into query_discovery loop")
            front_nodes = requests.get('http://' + discoveryip + ':8000/frontend').json()
            back_nodes = requests.get('http://' + discoveryip + ':8000/backend').json()
            return front_nodes, back_nodes
        except requests.ConnectionError:
            time.sleep(2)
            continue


# for x in range(0,10):
while True:
    time.sleep(2)
    front_nodes, back_nodes = query_discovery()
    logging.warning('Got front_nodes = %s, back_nodes = %s', front_nodes, back_nodes)
    for key, value in front_nodes.items():
        try:
            r = requests.post('http://'+value+':9000', data=back_nodes)
            logging.warning("POST to Frontend - SUCCESS - Elapsed: {0} ".format(r.elapsed))

        except requests.ConnectionError:
            logging.warning("POST to Frontend - FAILED")
