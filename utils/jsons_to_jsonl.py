import os, sys
from pathlib import Path
from tqdm import tqdm


def main(start: int, end: int) -> None:
    target_dir = Path('./')
    jsonl_file = Path(f'./{start}-{end}.jsonl')

    with open(jsonl_file, 'w', encoding='utf-8') as outfile:
        for i in tqdm(range(start, end + 1)):
            target_file = target_dir / f'[{i}]results.json'
            if target_file.exists():
                with open(target_file, 'r', encoding='utf-8') as fp:
                    content = fp.read()
                    if i != end:
                        content += '\n'
                    outfile.write(content)
                os.remove(target_file)


if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]))
