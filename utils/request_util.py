import requests


def build_session():
    session = requests.Session()
    return session


session = build_session()
