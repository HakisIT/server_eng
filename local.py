import requests

res = requests.get('http://192.168.1.35:9999/api/users/2')
print(res.json())