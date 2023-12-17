from tasks import answer
from tqdm import tqdm
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', required=True, type=int)
    parser.add_argument('-e', '--end', required=True, type=int)
    args = parser.parse_args()

    for _ in tqdm(range(args.start, args.end + 1)):
        answer.fetch_question_with_answer.delay(_)
