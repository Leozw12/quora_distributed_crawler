import traceback
import requests
from datetime import datetime
from main import app
from api.answer import fetch_answers_by_qid
from api.question import fetch_question_info_by_qid
from api.profile import fetch_user_info_by_uid
from api.comment import fetch_comments_by_aid


@app.task(acks_late=True)
def fetch_question_with_answer(qid: int) -> None:
    session: requests.Session = app.conf['session']

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

    # get question information
    result.update(**fetch_question_info_by_qid(session, qid))

    cursor = None

    try:
        while True:
            response = fetch_answers_by_qid(session, qid, cursor)

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
                    # get answer comments
                    new_answer.update(comments=get_all_comment(session, answer['id']))
                    result['answers'].append(new_answer)

                    # get asker info
                    if result['asker'] == {}:
                        result['asker'] = fetch_user_info_by_uid(session, answer['question']['asker']['uid'])

            if not data_connection['pageInfo']['hasNextPage']:
                break
            
            # update next page cursor
            cursor = data_connection['pageInfo']['endCursor']

    except Exception as e:
        # 记录异常堆栈到日志文件中
        now = datetime.now()
        with open(f'./{now.year}-{now.month}-{now.day}.log', 'a', encoding='utf-8') as out:
            out.write(f'{qid} {response.text}\n' + traceback.format_exc() + '\n')
        raise

    # TODO: How should I save the results?

    return result


def get_all_comment(session, aid: str):
    comments = []
    cursor = None

    while True:
        response = fetch_comments_by_aid(session, aid, cursor)
        comments_connection = response.json()['data']['node']['allCommentsConnection']

        for edge in comments_connection['edges']:
            comment_node = edge['node']
            user = comment_node['user']
            comments.append({
                'commentId': comment_node['commentId'],
                'creationTime': comment_node['creationTime'],
                'url': comment_node['url'],
                'author': {
                    'uid': user['uid'],
                    'profileUrl': user['profileUrl'],
                    'givenName': user['names'][0]['givenName'] if len(user['names']) > 0 else '',
                    'familyName': user['names'][0]['familyName'] if len(user['names']) > 0 else ''
                },
                'content': comment_node['contentQtextDocument']['legacyJson']
            })

        if not comments_connection['pageInfo']['hasNextPage']:
            break

        # update next page cursor
        cursor = comments_connection['pageInfo']['endCursor']

    return comments


def extract_answer(answer):
    """提取出answer中需要的数据"""
    return {
        'aid': answer['aid'],
        'url': answer['url'],
        'content': answer['content'],
        'author': {
            'uid': answer['author']['uid'],
            'givenName': answer['author']['names'][0]['givenName'] if len(answer['author']['names']) > 0 else '',
            'familyName': answer['author']['names'][0]['familyName'] if len(answer['author']['names']) > 0 else '',
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
