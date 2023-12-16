import json
import requests
from utils.common import get_quora_header, get_quora_cookie


def fetch_user_info_by_uid(session: requests.Session, uid: int):
    payload = {
        "queryName": "UserProfileCombinedListQuery",
        "variables": {
            "uid": uid,
            "after": '2',
            "first": 3,
            "order": 1
        },
        "extensions": {
            "hash": "2db78826756ddf25b6fd683a624a1dea9e308b17b2e91926c987c91ffd7c8580"
        }
    }

    response = session.post(
        'https://www.quora.com/graphql/gql_para_POST?q=UserProfileCombinedListQuery',
        data=json.dumps(payload), headers=get_quora_header(), cookies=get_quora_cookie()
    )

    user = response.json()['data']['user']

    return {
        'uid': uid,
        'givenName': user['names'][0]['givenName'] if len(user['names']) > 0 else '',
        'familyName': user['names'][0]['familyName'] if len(user['names']) > 0 else '',
        'isMachineAnswerBot': user['isMachineAnswerBot'],
    }
