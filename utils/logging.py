from datetime import datetime
from pathlib import Path


def log_to_file(s: str):
    now = datetime.now()
    Path('./logs').mkdir(parents=True, exist_ok=True)
    with open(f'./logs/{now.year}-{now.month}-{now.day}.log', 'a', encoding='utf-8') as out:
        out.write(f'{s}\n')
