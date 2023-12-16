import json
import requests
from utils.common import get_quora_header, get_quora_cookie


def fetch_comments_by_aid(session: requests.Session, id: str, cursor: int = None):
    payload = {
        "queryName": "AllCommentsListQuery",
        "variables": {
            "id": id,
            "after": cursor,
            "first": 100,
        },
        "extensions": {
            "hash": "7842e5b1f2eebdbf08ae89a7e29ec86d546f969e543a84f0c2683cfdd15eae96"
        }
    }

    return session.post( 
                        'https://www.quora.com/graphql/gql_para_POST?q=AllCommentsListQuery',
                        data=json.dumps(payload), headers=get_quora_header(), cookies=get_quora_cookie()
                        )
