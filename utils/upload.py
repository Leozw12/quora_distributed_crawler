import json
from .session_util import build_session_with_retry


url = "http://localhost:65534/upload"


def upload(data):
    files = {"file": (f'{data["qid"]}.json', json.dumps(data).encode('utf-8'), 'application/octet-stream')}
    response = build_session_with_retry(retries=3).post(url, files=files)
    response.raise_for_status()
