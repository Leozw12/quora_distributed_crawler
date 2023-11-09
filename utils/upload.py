import requests

url = "http://localhost:65534/upload"


def upload(file_path):
    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.post(url, files=files)
