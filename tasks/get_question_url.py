import json
import time
import random
from pathlib import Path
from utils.request_util import session
from main import app


@app.task(acks_late=True)
def get(keyword: str, cursor: str = '-1'):
    """
    Get question id and link

    Args:
        keyword: Keywords used to search
        cursor: Paginate skip
    """
    headers = json.loads(Path('./user/headers.json').read_text(encoding='utf-8'))

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
            "hash": ""
        }
    }
    payload['extensions']['hash'] = Path('./user/search_hash.txt').read_text(encoding='utf-8')

    session.cookies.update(json.loads(Path('./user/cookies.json').read_text(encoding='utf-8')))

    # 检查是否有数据
    response = session.post('https://www.quora.com/graphql/gql_para_POST?q=SearchResultsListQuery', headers=headers, json=payload)
    if response.json()['data']['searchConnection'] is None:
        return 'data null'

    while True:
        response = session.post('https://www.quora.com/graphql/gql_para_POST?q=SearchResultsListQuery', headers=headers,
                                json=payload)

        if (response.status_code == 404) or (response.json()['data']['searchConnection'] is None):
            time.sleep(random.randint(5, 8))
            continue

        data = response.json()['data']

        with open(f'../results/[{keyword}]results.txt', 'a', encoding='utf-8') as f:
            for edge in data['searchConnection']['edges']:
                f.write(f'{edge["node"]["question"]["qid"]} {edge["node"]["question"]["url"]}\n')

        cursor = data['searchConnection']['pageInfo']['endCursor']
        payload['variables']['after'] = cursor

        print(f'\rkeyword: {keyword} | cursor: {cursor}', end='', flush=True)

        # 分页结束
        if not data['searchConnection']['pageInfo']['hasNextPage']:
            break

    return {'keyword': keyword, 'end_cursor': cursor}


# if __name__ == '__main__':
#     print(get('hello'))
