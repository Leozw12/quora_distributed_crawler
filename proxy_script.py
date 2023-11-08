import json

from mitmproxy import http


def request(flow: http.HTTPFlow):
    req_url = flow.request.url
    if 'gql_para_POST?q=SearchResultsListQuery' in req_url:
        header_dict = dict(zip(flow.request.headers.keys(), flow.request.headers.values()))
        # 去除不需要的key
        header_dict.pop('cookie')
        header_dict.pop('content-length')
        # 保存到文件
        with open('./user/headers.json', 'w') as fp:
            json.dump(header_dict, fp)

        with open('./user/search_hash.txt', 'w') as fp:
            fp.write(json.loads(flow.request.text)['extensions']['hash'])

        # 获取cookie
        cookie_dict = dict(zip(flow.request.cookies.keys(), flow.request.cookies.values()))
        with open('./user/cookies.json', 'w') as fp:
            json.dump(cookie_dict, fp)

    if 'gql_para_POST?q=ContentLogMainQuery' in req_url:
        with open('./user/log_hash.txt', 'w') as fp:
            fp.write(json.loads(flow.request.text)['extensions']['hash'])

        # 获取cookie
        cookie_dict = dict(zip(flow.request.cookies.keys(), flow.request.cookies.values()))
        with open('./user/cookies.json', 'w') as fp:
            json.dump(cookie_dict, fp)

        header_dict = dict(zip(flow.request.headers.keys(), flow.request.headers.values()))
        # 去除不需要的key
        header_dict.pop('cookie')
        header_dict.pop('content-length')
        # 保存到文件
        with open('./user/headers.json', 'w') as fp:
            json.dump(header_dict, fp)


def response(flow: http.HTTPFlow):
    pass
