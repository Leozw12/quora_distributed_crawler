import json
import requests
from utils.common import get_quora_header, get_quora_cookie


def fetch_answers_by_qid(session: requests.Session, qid: int, cursor: int = None):
    payload = {
        "queryName": "QuestionAnswerPagedListQuery",
        "variables": {
            "qid": qid,
            "after": cursor,
            "first": 100,
            "forceScoreVersion": "hide_relevant_answers"
        },
        "extensions": {
            "hash": "8b794eb4b0c433bea1403c056e5811082342dc4cc0843ba84a8c25452630875d"
        }
    }

    return session.post( 
                        'https://www.quora.com/graphql/gql_para_POST?q=QuestionAnswerPagedListQuery',
                        data=json.dumps(payload), headers=get_quora_header(), cookies=get_quora_cookie()
                        )
