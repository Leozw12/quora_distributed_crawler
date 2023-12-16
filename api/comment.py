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


def fetch_reply_by_comment_id(session: requests.Session, cid: int, cursor: int = None):
    payload = {
        "queryName": "CommentRepliesListQuery",
        "variables": {
            "commentId": cid,
            "after": cursor,
            "first": 100,
            "requestType": None,
            "commentType": "answer_comment"
        },
        "extensions": {
            "hash": "65b10f19a7c88a44065f9fce075df7078831c52d3e251fd35eceb8dd3ad950ac"
        }
    }

    return session.post( 
                        'https://www.quora.com/graphql/gql_para_POST?q=CommentRepliesListQuery',
                        data=json.dumps(payload), headers=get_quora_header(), cookies=get_quora_cookie()
                        )
