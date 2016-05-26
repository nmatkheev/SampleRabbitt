import requests


discovery = 'http://127.0.0.1:8000'  # ---> argument 0

front_nodes = requests.get(discovery+'/frontend').json()
back_nodes = requests.get(discovery+'/backend').json()


for key,value in front_nodes.items():
    r = requests.post('http://'+value+':9000', data=back_nodes)
    print("Elapsed time: ", r.elapsed)