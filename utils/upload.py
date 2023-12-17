import json
import requests


url = "http://localhost:65534/upload"


def upload(data):
    files = {"file": (f'{data["qid"]}.json', json.dumps(data).encode('utf-8'), 'application/octet-stream')}
    response = requests.post(url, files=files)
    response.raise_for_status()
