from api_tasks import get_question_url, get_answers
from tqdm import tqdm
import pandas as pd

if __name__ == '__main__':
    # result = get_question_url.run.delay('hello')
    # result = get_answers.run.delay('155166933')
    # print(result)

    # with open(r'C:\Users\Mechrevo\Desktop\[x] professional_field_word.txt', 'r', encoding='utf-8') as f:
    #     for keyword in tqdm(f):
    #         if keyword.strip() != '':
    #             get_question_url.run.delay(keyword.strip())

    df = pd.read_parquet(r'C:\Users\Mechrevo\Desktop\quora_url_id.parquet')
    for _ in tqdm(df.iloc[0:1000].values):
        get_answers.run.delay(_[0])
