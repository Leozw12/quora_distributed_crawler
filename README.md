# quora_distributed_crawler 
This project is a distributed web crawler, which is specially developed for crawling data from Quora.com.

## Getting Started
### Prerequisites
Server message queuing middleware, using rabbitmq or redis.
| Dependency | Version        |
|------------|----------------|
| Python     | 3.11 or higher |
| RabbitMQ   | latest         |
| Redis      | latest         |

### Installation
```
git clone https://github.com/LxYxvv/quora_distributed_crawler.git
cd quora_distributed_crawler
pip install -r requirements.txt
```

### Start server
```
cd quora_distributed_crawler/server
python main.py
```

### Configuration worker
Set the `broker_url` in the **config.py** file to your message middleware address.
Set the `worker_concurrency` worker process to 2, to prevent too many and frequent crawler requests.
Set the `url` in the **utils/upload.py**

### Submit tasks
How to submit a task to the queue?<br />
Please refer to [celery doc](https://docs.celeryq.dev/en/stable/userguide/calling.html). need to configure the  `broker_url` of the server **config.py**

### Start worker
```
python main.py
```
### Start worker by android
Download ZeroTermux https://github.com/hanxinhao000/ZeroTermux/releases
```
pkg update && pkg upgrade
pkg install python3
```
Then [Installation](#installation) > [Configuration worker](#configuration-worker) > [Start worker](#start-worker)

