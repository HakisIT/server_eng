import requests

res = requests.get('http://192.168.1.35:9999/api/words/178')
print(res.json())