import json
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import pyarrow.parquet as pq
import pyarrow as pa


def main(start: int, end: int) -> None:
    target_dir = Path('./')
    parquet_file = f'./{start}-{end}.parquet'

    # 初始化 ParquetWriter
    writer = None

    for i in tqdm(range(start, end + 1)):
        target_file = target_dir / f'[{i}]results.json'
        if target_file.exists():
            with open(target_file, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                data_normalize = pd.json_normalize(data)

                table = pa.Table.from_pandas(data_normalize)

                if writer is None:
                    writer = pq.ParquetWriter(parquet_file, table.schema)

                writer.write_table(table)


if __name__ == '__main__':
    main(902, 903)
