import json
import fire
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from datasets import load_dataset
from tqdm import tqdm


def convert_to_markdown(data: dict | str) -> str:
    """ Convert Quora data to markdown format.

    Args:
        data (dict): Quora data

    Returns:
        str: markdown string
    """
    if isinstance(data, str):
        data = json.loads(data)

    markdown = ''
    code_block = ''

    for section_index, section in enumerate(data['sections']):
        # Add quote
        if section['quoted'] and section['type'] != 'code':
            markdown += "> "

        # Add indentation based on the section depth
        if section['type'] != 'code':
            markdown += (' ' * 4 * section['indent'])

        match section['type']:
            case 'heading':
                markdown += f"# {section['spans'][0]['text']}"

            case 'plain' | 'ordered-list' | 'unordered-list':
                if section['type'] == 'ordered-list':
                    markdown += "1. "

                if section['type'] == 'unordered-list':
                    markdown += "- "

                for span in section['spans']:
                    text = span['text'] if span['text'].strip() == '' else span['text'].strip()

                    # The font is bold and italic
                    if span['modifiers'].get('bold') and span['modifiers'].get('italic'):
                        text = f"***{text}***"

                    # The font is bold
                    elif span['modifiers'].get('bold'):
                        text = f"**{text}**"

                    # The font is italic
                    elif span['modifiers'].get('italic'):
                        text = f"*{text}*"

                    # This is a mathematical formula
                    elif span['modifiers'].get('math'):
                        text = f"${text}$"

                    if 'link' in span['modifiers']:
                        if span['modifiers']['link']['type'] == 'user':
                            text = f"[@{text}]({span['modifiers']['link']['url']})"
                        else:
                            text = f"[{text}]({span['modifiers']['link']['url']})"

                    markdown += text

            case 'yt-embed':
                video_url = section['spans'][0]['modifiers']['embed']['url']

                parsed_url = urlparse(video_url)
                query_params = parse_qs(parsed_url.query)
                markdown += f'<iframe height="500" src="https://www.youtube.com/embed/{query_params.get('v', [0])[-1]}"></iframe>'

            case 'hyperlink_embed':
                markdown += f"[{section['spans'][0]['modifiers']['embed']['title']}]({section['spans'][0]['modifiers']['embed']['url']})"

            case 'code':
                code_block += f"{' ' * 4 *  section['indent']}{section['spans'][0]['text']}\n"

                if not (section_index < len(data['sections']) - 1 and data['sections'][section_index + 1]['type'] == 'code'):
                    markdown += f"```\n{code_block}```"
                    code_block = ''

        markdown += "\n\n"

    return markdown.strip()


def comments_handler(comments, prev_id):
    expanded_comments = []
    floor_index = 1
    for comment in sorted(comments, key=lambda x: x['creationTime']):
        if comment['content'].strip() != '':
            expanded_comments.append({
                '楼ID': f"{prev_id}_{floor_index}",
                '回复': convert_to_markdown(comment['content']),
                '扩展字段': json.dumps({
                    '回复人': f'{comment['author']['givenName']} {comment['author']['familyName']}'.strip(),
                    '回复时间': datetime.fromtimestamp(comment['creationTime'] / 1000_000).strftime('%Y%m%d %H:%M:%S'),
                    '引用ID': prev_id,
                    '源链接': f'https://quora.com{comment["url"]}'
                }, ensure_ascii=False)
            })

        if comment.get('comments', []):
            expanded_comments.extend(comments_handler(
                comment['comments'], f"{prev_id}_{floor_index}" if comment['content'].strip() != '' else prev_id))

        floor_index += 1

    return expanded_comments


def quora_format(row):
    op = {
        'ID': row['qid'],
        '主题': convert_to_markdown(row['title']),
        '来源': "Quora",
        '回复': [],
        '时间': datetime.fromtimestamp(row['creationTime'] / 1000_000).strftime('%Y%m%d'),
        '元数据': {
            '发帖时间': datetime.fromtimestamp(row['creationTime'] / 1000_000).strftime('%Y%m%d %H:%M:%S'),
            '回复数': row['numAnswers'],
            '扩展字段': json.dumps({
                '源链接': f'https://quora.com{row['url']}?no_redirect=1',
                '关注数量': row['followerCount'],
                '查看数量': row['viewCount'],
                '机器回复数量': row['numMachineAnswers']
            }, ensure_ascii=False)
        }
    }

    floor_index = 1
    for answer in sorted(json.loads(row['answers']), key=lambda x: x['creationTime']):
        if answer['content'] is None:
            continue

        reply = {
            '楼ID': str(floor_index),
            '回复': convert_to_markdown(answer['content']),
            '扩展字段': {
                '回复人': f'{answer['author']['givenName']} {answer['author']['familyName']}'.strip(),
                '回复时间': datetime.fromtimestamp(answer['creationTime'] / 1000_000).strftime('%Y%m%d %H:%M:%S'),
                '源链接': f'https://quora.com{answer['url']}',
            }
        }

        if answer.get('comments', []):
            reply['扩展字段']['子回复'] = comments_handler(answer['comments'], floor_index)

        reply['扩展字段'] = json.dumps(reply['扩展字段'], ensure_ascii=False)
        op['回复'].append(reply)

        floor_index += 1

    return op


def process(split: str = 'train', output_dir: str = './quora_datas', max_size_mb: int = 500):
    file_index = 1
    max_size_bytes = max_size_mb * 1024 * 1024
    ds = load_dataset('LxYxvv/quora_qa', split=split, streaming=True)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for row in tqdm(ds):
        if row['title'] is None or row['numAnswers'] == 0:
            continue

        formated_data = json.dumps(quora_format(row), ensure_ascii=False)

        formated_data_size = len(formated_data.encode('utf-8'))

        of_path = output_dir / Path(f'quora_data_{file_index}.jsonl')
        if of_path.exists() and (of_path.stat().st_size + formated_data_size) > max_size_bytes:
            file_index += 1
            of_path = output_dir / Path(f'quora_data_{file_index}.jsonl')

        with of_path.open('a', encoding='utf-8') as of:
            of.write(formated_data + '\n')


if __name__ == '__main__':
    fire.Fire(process)
