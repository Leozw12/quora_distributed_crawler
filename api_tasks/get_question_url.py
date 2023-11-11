import time
import os
import random

import requests.exceptions

from utils.request_util import session
from main_api import app
from utils.upload import upload


@app.task(acks_late=True)
def run(keyword: str):
    res = get(keyword)
    path = f'./results/[{keyword}]results.txt'
    os.makedirs('./results', exist_ok=True)
    if res != 'data null':
        with open(path, 'w', encoding='utf-8') as f:
            f.write(res)
        upload(path)
        os.remove(path)
    print(f'[{keyword}]Upload results ok')


def get(keyword: str, cursor: str = '-1'):
    """
    Get question id and link

    Args:
        keyword: Keywords used to search
        cursor: Paginate skip
    """
    headers = {
        "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "content-type": "application/json",
        "quora-page-creation-time": "1699449946230898",
        "quora-revision": "a4036a937a422c174c6e1c0d44483e15f19fab88",
        "quora-broadcast-id": "main-w-chan60-8888-react_gqdcxcrnikdfumri-qMjE",
        "quora-formkey": "30448ffe40b90d6d9ed3ea23ac752cca",
        "quora-canary-revision": "false",
        "quora-window-id": "react_gqdcxcrnikdfumri",
        "sec-ch-ua-platform": "\"Windows\"",
        "accept": "*/*",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    }

    payload = {
        "queryName": "SearchResultsListQuery",
        "variables": {
            "query": keyword,
            "disableSpellCheck": None,
            "resultType": "question",
            "author": None,
            "time": "all_times",
            "first": 10,
            "after": cursor,
            "tribeId": None
        },
        "extensions": {
            "hash": "c53ad81a8c02914d793df0789dec982aaad673436bff71f4461e1b502c5326f3"
        }
    }

    session.cookies.update(
        {
            "m-login": "0",
            "m-b": "sXahg6VVl0RJuDqNOWJlTQ==",
            "m-b_lax": "sXahg6VVl0RJuDqNOWJlTQ==",
            "m-b_strict": "sXahg6VVl0RJuDqNOWJlTQ==",
            "m-s": "YbAlBDLJzWvTfsE02PAnXA==",
            "m-uid": "None",
            "m-theme": "light",
            "m-dynamicFontSize": "regular"
        }
    )

    # 检查是否有数据
    while True:
        try:
            response = session.post('https://www.quora.com/graphql/gql_para_POST?q=SearchResultsListQuery',
                                    headers=headers,
                                    json=payload, timeout=5)
        except requests.exceptions.Timeout:
            print(f'\rkeyword: {keyword} | requests timeout', flush=True)
            time.sleep(3)
            continue

        if response.status_code == 404:
            continue
        if response.json()['data']['searchConnection'] is None:
            print(f'\rkeyword: {keyword} | data null', flush=True)
            return 'data null'
        break

    result = ''

    while True:
        try:
            response = session.post('https://www.quora.com/graphql/gql_para_POST?q=SearchResultsListQuery',
                                    headers=headers,
                                    json=payload,
                                    timeout=5)
        except requests.exceptions.Timeout:
            print(f'\rkeyword: {keyword} | requests timeout', flush=True)
            time.sleep(3)
            continue

        try:
            if (response.status_code != 200) or (response.json()['data']['searchConnection'] is None):
                # print(response.json()['data']['searchConnection'])
                time.sleep(random.randint(5, 8))
                continue
        except:
            continue

        data = response.json()['data']

        # with open(f'../results/[{keyword}]results.txt', 'a', encoding='utf-8') as f:
        for edge in data['searchConnection']['edges']:
            # f.write(f'{edge["node"]["question"]["qid"]} {edge["node"]["question"]["url"]}\n')
            result += f'{edge["node"]["question"]["qid"]} {edge["node"]["question"]["url"]}\n'

        cursor = data['searchConnection']['pageInfo']['endCursor']
        payload['variables']['after'] = cursor

        print(f'\rkeyword: {keyword} | cursor: {cursor}', end='', flush=True)

        # 分页结束
        if not data['searchConnection']['pageInfo']['hasNextPage']:
            break
    print()
    return result


if __name__ == '__main__':
    get('first')
