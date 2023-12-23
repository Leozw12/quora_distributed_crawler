# https://docs.celeryq.dev/en/stable/userguide/configuration.html

# 消息中间件
broker_url = 'redis://:123456@localhost:6379/0'

# 结果保存后端
# result_backend = 'redis://:123456@localhost:6379/1'

# 时间区域
timezone = 'Asia/Shanghai'

# 工作进程数
worker_concurrency = 2

broker_connection_retry_on_startup = True

broker_pool_limit = 5

worker_max_tasks_per_child = 500

task_reject_on_worker_lost = True

task_acks_late = True

worker_hijack_root_logger = False

worker_cancel_long_running_tasks_on_connection_loss = True