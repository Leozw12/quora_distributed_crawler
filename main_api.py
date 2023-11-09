import os
import platform
import sys
from pathlib import Path

from celery import Celery
from utils import check_connect

app = Celery('quora-distributed-crawl', include=['api-tasks.get_answers', 'api-tasks.get_question_url'])
app.config_from_object('config')

if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    # 为win平台添加兼容环境变量
    if platform.system().lower() == 'windows':
        os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
        print('Forked by multiprocessing = 1')

    # 检查是否可连通Quora
    if not check_connect.is_connectable():
        print('Unable to connect to www.quora.com.')
        sys.exit(1)
    else:
        print('Can connect to www.quora.com.')

    app.start(['-A', 'main-api', 'worker', '--loglevel=info'])
