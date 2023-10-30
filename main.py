from celery import Celery

app = Celery('quora-dist-crawl', include=['tasks'])
app.config_from_object('celeryconfig')


if __name__ == '__main__':
    app.start(['-A', 'main', 'worker', '-loglevel=info', '--autoreload'])
