import json
import os
import time
from pathlib import Path
from main import app, build_chrome_driver
from utils.request_util import session
from tqdm import tqdm


@app.task
def get(qid: int | str, url: str, cursor: str = '-1'):
    """
    Get question information and all answer.

    Args:
        qid: Question unique identification
        url: Question url
        cursor: Paginate skip
    """
    url = url + '/log' if url.startswith('https') else f'https://www.quora.com{url}/log'
    with build_chrome_driver(os.getenv('selenium_proxy_port'))(url) as driver:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    headers = json.loads(Path('./user/headers.json').read_text(encoding='utf-8'))

    payload = {
        "queryName": "ContentLogMainQuery",
        "variables": {
            "entityType": "question",
            "oid": qid,
            "first": 10,
            "after": cursor
        },
        "extensions": {
            "hash": ""
        }
    }
    payload['extensions']['hash'] = Path('./user/log_hash.txt').read_text(encoding='utf-8')

    session.cookies.update(json.loads(Path('./user/cookies.json').read_text(encoding='utf-8')))

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

    progress = tqdm(desc='任务' + str(qid) + '进行中', leave=False)

    while True:
        response = session.post('https://www.quora.com/graphql/gql_para_POST?q=ContentLogMainQuery', headers=headers, json=payload)

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


# if __name__ == '__main__':
#     print(len(get(5459462, '/How-do-I-find-the-equivalent-resistance-between-A-and-B')['answers']))
