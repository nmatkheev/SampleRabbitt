import requests
import grequests
import logging
import time


DEBUG = False

if DEBUG:
    network = '127.0.0.'
    logroot = './Logs/'
else:
    network = '172.17.0.'
    logroot = '/mnt/dat/'


def exception_handler(request, exception):
    logging.warning("Request: %s", exception)


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


# ----------------------------------------------------------------------------------------
# 1 - retrieve own ip and then - setup logging
current_node_ip = return_ip()
num = 0
while True:
    if is_exists(logroot+'client_{0}-launch{1}.log'.format(current_node_ip, num)):
        num += 1
        continue
    else:
        break
logpath = logroot+'client_{0}-launch{1}.log'.format(current_node_ip, num)
# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.WARNING)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=logpath, level=logging.DEBUG)
# ----------------------------------------------------------------------------------------
# 2 - find discovery's ip

discoveryip = find_discovery()
logging.debug("found discovery - %s", discoveryip)


def query_discovery():
    while True:
        try:
            # logging.warning("Entered into query_discovery loop")
            _front_nodes = requests.get('http://' + discoveryip + ':8000/frontend').json()
            _back_nodes = requests.get('http://' + discoveryip + ':8000/backend').json()

            if len(_back_nodes) < 2 or len(_front_nodes) < 1:
                continue

            return _front_nodes, _back_nodes
        except requests.ConnectionError:
            time.sleep(2)
            continue


while True:
# for x in range(0, 2):
    def elapsed(r, *args, **kwargs):
        logging.warning("Elapsed: %s, Status: %s, URL: %s", r.elapsed, r.status_code, r.url)

    front_nodes, back_nodes = query_discovery()
    logging.warning('Got front_nodes = %s, back_nodes = %s', front_nodes, back_nodes)
    for key, value in front_nodes.items():
        # reqs = [grequests.post('http://'+value+':9000', data={'1': l[1]}, hooks=dict(response=elapsed)) for l in back_nodes.items()]

        logging.warning("=======================  Start of request bunch  =========================")

        reqplan = [0 if x < 7 else 1 for x in range(0,12)]

        reqs = [grequests.post('http://'+value+':9000', data={'1': back_nodes['{0}'.format(r)]}, hooks=dict(response=elapsed)) for r in reqplan]

        grequests.map(reqs, exception_handler=exception_handler)

        logging.warning("========================  End of request bunch  =========================")
        time.sleep(3)

