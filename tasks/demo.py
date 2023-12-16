import sys
import time
import tqdm
from main import app


@app.task(acks_late=True)
def demo():
    # for _ in tqdm.trange(100):
    time.sleep(30)
    return 'Hello World!'
