import requests

for i in range(100):
    requests.post('http://localhost:8000/', json={'msg': f'msg{i}'})

