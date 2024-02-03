import json
import time
import requests
from utils.common import get_quora_header, get_quora_cookie


def fetch_question_info_by_qid(session: requests.Session, qid: int):
    payload = {
        "queryName": "ContentLogMainQuery",
        "variables": {
            "oid": qid,
            "after": '2',
            "first": 3,
            "entityType": "question"
        },
        "extensions": {
            "hash": "a96a8c2b005f2946bd59db3339fddb88ef5ce8cecfe9bc5f0759166f3f2e2aba"
        }
    }

    continue_count = 0

    while True:
        response = session.post(
            'https://www.quora.com/graphql/gql_para_POST?q=ContentLogMainQuery',
            data=json.dumps(payload), headers=get_quora_header(), cookies=get_quora_cookie()
        )

        if 'application/json' in response.headers.get('Content-Type', ''):
            break
        
        continue_count += 1
        print(f'api/question 29 line - response not is json, count:{continue_count}')
        time.sleep(1)

    contentObject = response.json()['data']['contentObject']

    return {
        'qid': qid,
        'url': contentObject['url'],
        'title': contentObject['title'],
        'viewCount': contentObject['viewCount'],
        'followerCount': contentObject['followerCount'],
        'isLocked': contentObject['isLocked'],
        'isTrendyQuestion': contentObject['isTrendyQuestion'],
        'creationTime': contentObject['creationTime'],
        'asker': {'uid': contentObject['asker']['uid']}
    }
