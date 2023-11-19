# https://docs.celeryq.dev/en/stable/userguide/configuration.html

# 消息中间件
BROKER_URL = 'redis://:123456@localhost:6379/0'
# 结果保存后端
# CELERY_RESULT_BACKEND = 'redis://:123456@localhost:6379/1'
# 时间区域
CELERY_TIMEZONE = 'Asia/Shanghai'
# 工作进程数
CELERYD_CONCURRENCY = 1

CELERYD_MAX_TASKS_PER_CHILD = 20

CELERY_REJECT_ON_WORKER_LOST = False
CELERY_ACKS_LATE = True


BROKER_TRANSPORT_OPTIONS = {
    'socket_timeout': 300,          # 建立连接后的套接字超时
    'socket_connect_timeout': 30   # 连接Redis服务器的超时
}
