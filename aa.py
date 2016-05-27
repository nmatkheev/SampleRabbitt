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


def is_exists(logname):
    import os
    return os.path.isfile(os.path.curdir+'/'+logname)


current_node_ip = return_ip()

num = 0

while True:
    if is_exists('backend_{0}-launch{1}.log'.format(current_node_ip, num)):
        num += 1
        continue
    else:
        break

print(num)