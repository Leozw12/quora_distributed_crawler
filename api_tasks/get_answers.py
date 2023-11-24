import os
import time
from main import app
from utils.request_util import session
from tqdm import tqdm
import requests.exceptions

from utils.upload import upload
import json


@app.task(acks_late=True)
def run(keyword: str):
    res = get(keyword)
    path = f'./results/[{keyword}]results.txt'
    os.makedirs('./results', exist_ok=True)
    if res != 'data null':
        with open(path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(res))
        upload(path)
        os.remove(path)
    print(f'[{keyword}]Upload results ok')


def get(qid: int | str, cursor: str = '-1'):
    """
    Get question information and all answer.

    Args:
        qid: Question unique identification
        cursor: Paginate skip
    """
    headers = {
        "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "content-type": "application/json",
        "quora-page-creation-time": "1699448496586354",
        "quora-revision": "a4036a937a422c174c6e1c0d44483e15f19fab88",
        "quora-broadcast-id": "main-w-chan60-8888-react_xyyurmwcguleitze-cvMU",
        "quora-formkey": "11619dd1f8d419325d0b8d1eb98f51be",
        "quora-canary-revision": "false",
        "quora-window-id": "react_xyyurmwcguleitze",
        "sec-ch-ua-platform": "\"Windows\"",
        "accept": "*/*",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    }

    payload = {
        "queryName": "ContentLogMainQuery",
        "variables": {
            "entityType": "question",
            "oid": qid,
            "first": 10,
            "after": cursor
        },
        "extensions": {
            "hash": "ca79f83cf825739cbbd705bf2558110543d18269ceefe159d8db9e52fc5f16f3"
        }
    }

    session.cookies.update(
        {
            "m-login": "0",
            "m-b": "Cgc5Wt927tJE7drbFNpc4A==",
            "m-b_lax": "Cgc5Wt927tJE7drbFNpc4A==",
            "m-b_strict": "Cgc5Wt927tJE7drbFNpc4A==",
            "m-s": "S_JEpyNiQd2xvqTF0G7C7A==",
            "m-uid": "None",
            "m-theme": "light",
            "m-dynamicFontSize": "regular"
        }
    )

    # 输出格式
    result = {
        'qid': 0,
        'url': '',
        'title': '',
        'asker': {},
        'creationTime': 0,
        'followerCount': 0,
        'isLocked': False,
        'viewCount': 0,
        'answers': []
    }

    progress = tqdm(desc='任务' + str(qid) + '进行中')

    while True:
        try:
            response = session.post('https://www.quora.com/graphql/gql_para_POST?q=ContentLogMainQuery',
                                    headers=headers,
                                    json=payload,
                                    timeout=20)
        except requests.exceptions.Timeout:
            print(f'\rkeyword: {qid} | requests timeout', flush=True)
            time.sleep(3)
            continue

        if response.status_code == 404:
            time.sleep(3)
            continue

        if response.status_code != 200:
            break

        data = response.json()['data']

        # 添加问题信息
        if result['qid'] == 0:
            result['qid'] = data['contentObject']['qid']
            result['url'] = data['contentObject']['url']
            result['title'] = data['contentObject']['title']
            result['creationTime'] = data['contentObject']['creationTime']
            result['followerCount'] = data['contentObject']['followerCount']
            result['isLocked'] = data['contentObject']['isLocked']
            result['viewCount'] = data['contentObject']['viewCount']

        for edge in data['contentObject']['logConnection']['edges']:
            if edge['node']['__typename'] == 'AttachAnswerOperation' and not edge['node']['answer']['isDeleted']:
                answer = {
                    'opid': edge['node']['opid'],
                    'time': edge['node']['time'],
                    'url': edge['node']['answer']['permaUrl'],
                    'content': edge['node']['answer']['content'],
                    'isSensitive': edge['node']['answer']['isSensitive']
                }
                if edge['node']['responsibleUser'] is not None:
                    answer['author'] = {
                        'uid': edge['node']['responsibleUser']['uid'],
                        'givenName': edge['node']['responsibleUser']['names'][0]['givenName'],
                        'familyName': edge['node']['responsibleUser']['names'][0]['familyName'],
                        'profileUrl': edge['node']['responsibleUser']['profileUrl']
                    }
                result['answers'].append(answer)
            elif edge['node']['__typename'] == 'AddQuestionOperation':
                result['asker'] = {
                    'uid': edge['node']['responsibleUser']['uid'],
                    'givenName': edge['node']['responsibleUser']['names'][0]['givenName'],
                    'familyName': edge['node']['responsibleUser']['names'][0]['familyName'],
                    'profileUrl': edge['node']['responsibleUser']['profileUrl']
                }

        # 切换分页最后指向
        end_cursor = data['contentObject']['logConnection']['pageInfo']['endCursor']
        payload['variables']['after'] = end_cursor

        progress.n = int(end_cursor)
        progress.refresh()
        # 分页结束
        if not data['contentObject']['logConnection']['pageInfo']['hasNextPage']:
            break

    # print(json.dumps(result))
    return result


if __name__ == '__main__':
    print(run(155166933))
