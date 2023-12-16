import json
import os
import platform
import sys
from pathlib import Path
from celery import Celery
from utils import check_connect, session_util


app = Celery('quora-distributed-crawl', include=['tasks.demo', 'tasks.answer'])
app.config_from_object('config')

# 为每个worker构建一个请求会话
session = session_util.build_session_with_retry()
app.conf.update(session=session)


def main():
    os.chdir(Path(__file__).parent)

    # 为celery在windows平台中添加兼容
    if platform.system().lower() == 'windows':
        os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
        print('Forked by multiprocessing = 1')

    # 检查是否可连通Quora
    if check_connect.is_connectable():
        print('Can connect to www.quora.com.')
    else:
        print('Unable to connect to www.quora.com.')
        sys.exit(1)


if __name__ == '__main__':
    main()
    app.start(['-A', 'main', 'worker', '--loglevel=info'])
