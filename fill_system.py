import requests

for i in range(1,101):
    res = requests.post('http://localhost:8000/', json={'msg': f'msg{i}'})
    print(res.json())

