import time
import traceback
import requests
from main import app
from api.answer import fetch_answers_by_qid
from api.question import fetch_question_info_by_qid
from api.profile import fetch_user_info_by_uid
from api.comment import fetch_comments_by_aid, fetch_reply_by_comment_id
from utils.logging_util import log_to_file
from utils.upload import upload
from utils.session_util import build_session_with_retry


@app.task(bind=True, acks_late=True, ignore_result=True)
def fetch_question_with_answer(self, qid: int) -> None:
    session: requests.Session = app.conf['session']
    # TODO: Temporary solution, because multiple processes share a session, resulting in the problem of slow request.
    # session: requests.Session = build_session_with_retry()

    # output formatte
    result = {
        'qid': None,
        'url': '',
        'title': '',
        'creationTime': 0,
        'followerCount': 0,
        'viewCount': 0,
        'numAnswers': 0,
        'numMachineAnswers': 0,
        'isLocked': False,
        'isTrendyQuestion': False,
        'asker': {},
        'answers': []
    }

    cursor = None

    try:
        # get question information
        result.update(**fetch_question_info_by_qid(session, qid))

        # get asker info
        result['asker'] = fetch_user_info_by_uid(session, result['asker']['uid'])

        continue_count = 0

        while True:
            response = fetch_answers_by_qid(session, qid, cursor)

            if response.json().get('data', None) is None:
                continue_count += 1

                print(f'tasks/answer 51 line - data/comment/repliesConnection, count: {continue_count}')

                if continue_count >= 10:
                    return

                time.sleep(1)
                continue

            data_connection = response.json()['data']['question']['pagedListDataConnection']

            edges = data_connection['edges']
            for edge in edges:
                node = edge['node']
                node_type = node['__typename']

                # header meta data
                if node_type == 'QuestionAnswerHeaderItem':
                    result['numAnswers'] = node['numAnswers']
                    result['numMachineAnswers'] = node['numMachineAnswers']

                # answer item
                if node_type == 'QuestionAnswerItem2':
                    answer = node['answer']
                    new_answer = extract_answer(answer)
                    
                    if new_answer["numComments"] > 0:
                        # get answer comments
                        new_answer.update(comments=get_all_comment(session, answer['id']))
                    
                    result['answers'].append(new_answer)

            time.sleep(1)

            if not data_connection['pageInfo']['hasNextPage']:
                break

            # update next page cursor
            cursor = data_connection['pageInfo']['endCursor']

    except requests.exceptions.RetryError as e:
        # Log the exception stack to the log file
        log_to_file(f'{qid}\n' + traceback.format_exc())
        # back task
        back_queue(self)
        raise

    # upload result
    try:
        upload(result)
    except requests.HTTPError as e:
        # back task
        back_queue(self)
        raise

    return qid


def back_queue(celery_instance):
    """Back task to the queue."""
    routing_key = celery_instance.request.delivery_info['routing_key']
    exchange = celery_instance.request.delivery_info['exchange']
    args = celery_instance.request.args
    kwargs = celery_instance.request.kwargs
    new_task = celery_instance.app.send_task(celery_instance.name, args=args, kwargs=kwargs, exchange=exchange, queue=routing_key, reject_on_worker_lost=True)
    print(f'[{celery_instance.request.id}]: ERROR || NEW-TASK-ID:{new_task}')


def extract_answer(answer):
    """Filter out the data we need from the answer data."""
    return {
        'aid': answer['aid'],
        'url': answer['url'],
        'content': answer['content'],
        'author': {
            'uid': answer['author']['uid'],
            'givenName': answer['author']['names'][0]['givenName'] if len(answer['author'].get('names', [])) > 0 else '',
            'familyName': answer['author']['names'][0]['familyName'] if len(answer['author'].get('names', [])) > 0 else '',
            'isMachineAnswerBot': answer['author']['isMachineAnswerBot'],
            'profileUrl': answer['author']['profileUrl']
        },
        'isSensitive': answer['isSensitive'],
        'isShortContent': answer['isShortContent'],
        'creationTime': answer['creationTime'],
        'numViews': answer['numViews'],
        'numUpvotes': answer['numUpvotes'],
        'numShares': answer['numShares'],
        'numComments': answer['numDisplayComments'],
        'comments': []
    }


def extract_comment(comment):
    """Filter out the data we need from the comment data."""
    comment_node = comment['node']
    user = comment_node['user']
    return {
        'commentId': comment_node['commentId'],
        'creationTime': comment_node['creationTime'],
        'url': comment_node['url'],
        'author': {
            'uid': user['uid'],
            'profileUrl': user['profileUrl'],
            'givenName': user['names'][0]['givenName'] if user and len(user.get('names', [])) > 0 else '',
            'familyName': user['names'][0]['familyName'] if user and len(user.get('names', [])) > 0 else ''
        },
        'content': comment_node['contentQtextDocument']['legacyJson'] if comment_node['contentQtextDocument'] is not None else '' 
    }


def get_all_reply(session, cid: int):
    replys = []
    cursor = None

    continue_count = 0

    while True:
        response = fetch_reply_by_comment_id(session, cid, cursor)

        if response.json().get('data', {}).get('comment', {}).get('repliesConnection', {}):
            continue_count += 1

            print(f'tasks/answer 160 line - data/comment/repliesConnection, count: {continue_count}')

            if continue_count >= 10:
                return

            time.sleep(1)
            continue

        replies_connection = response.json()['data']['comment']['repliesConnection']

        for edge in replies_connection['edges']:
            reply = extract_comment(edge)

            # Is there a next level reply?
            if len(edge['node']['repliesConnection']['edges']) > 0:
                reply.update(comments=get_all_reply(session, edge['node']['commentId']))

            replys.append(reply)

        time.sleep(1)

        if not replies_connection['pageInfo']['hasNextPage']:
            break

        # update next page cursor
        cursor = replies_connection['pageInfo']['endCursor']

    return replys


def get_all_comment(session, aid: str):
    comments = []
    cursor = None

    continue_count = 0

    while True:
        response = fetch_comments_by_aid(session, aid, cursor)

        if response.json().get('data', {}).get('node', {}).get('allCommentsConnection', {}):
            continue_count += 1
            print(f'tasks/answer 194 line - data/node/allCommentsConnection, count: {continue_count}, id: {aid}')
            
            if continue_count >= 10:
                return

            time.sleep(1)
            continue

        comments_connection = response.json()['data']['node']['allCommentsConnection']

        for edge in comments_connection['edges']:
            comment = extract_comment(edge)

            # Is there a next level reply?
            if len(edge['node']['repliesConnection']['edges']) > 0:
                comment.update(comments=get_all_reply(session, edge['node']['commentId']))

            comments.append(comment)

        time.sleep(1)

        if not comments_connection['pageInfo']['hasNextPage']:
            break

        # update next page cursor
        cursor = comments_connection['pageInfo']['endCursor']

    return comments
