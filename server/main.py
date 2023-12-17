import os
from pathlib import Path
from typing import Any
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
import uvicorn
import aiofiles
import redis


app = FastAPI(redoc_url=None)


class Question(BaseModel):
    qid: int
    url: str
    title: Any
    asker: Any
    creationTime: int
    followerCount: int
    isLocked: bool
    isTrendyQuestion: bool
    viewCount: int
    numAnswers: int
    numMachineAnswers: int
    answers: Any


def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size


# 字节数转换为合适大小单位
def convert_bytes(byte_size):
    # 定义单位
    units = ['B', 'KB', 'MB', 'GB', 'TB']

    # 选择合适的单位
    unit_index = 0
    while byte_size > 1024 and unit_index < len(units) - 1:
        byte_size /= 1024.0
        unit_index += 1

    result = f"{byte_size:.2f} {units[unit_index]}"
    return result


def count_small_files(directory):
    count = 0

    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            file_size = os.path.getsize(filepath)

            # 检查文件大小是否小于 1KB
            if file_size < 1024:
                count += 1

    return count


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    save_path = "./results/" + file.filename

    if not file.filename.endswith('.json'):
        return JSONResponse(status_code=500, content="Data format error.")
    
    data = await file.read()
    
    # Check json structure
    try:
        Question.model_validate_json(data)
    except ValidationError as e:
       return JSONResponse(status_code=500, content="Data format error.")

    # save to disk
    async with aiofiles.open(save_path, "wb") as out:
        await out.write(data)

    return {"message": "Upload successfully."}


# @app.get("/list/complete") 
# async def get_complete_list():
#     file_list = [file.name for file in Path('./results').glob('*') if file.is_file().]
#     id_list = []

#     return id_list


# @app.get("/info")
# async def get_info():
#     rc = redis.Redis(host='localhost', password='hP@9lRv2QxJ_2JreGx', port=6379, db=0)
#     try:
#         queue_num = rc.llen('celery')
#     except redis.RedisError:
#         queue_num = 0
#     finally:
#         rc.connection_pool.disconnect()

#     completion_num = len(await get_complete_list())
#     less_than_1kb = count_small_files('..')
#     less_than_1kb_ratio = less_than_1kb / completion_num

#     return {
#         'queue_num': queue_num,
#         'completion_num': completion_num,
#         'completion_size': convert_bytes(get_directory_size('..')),
#         'less_than_1kb': less_than_1kb,
#         'less_than_1kb_ratio': round(less_than_1kb_ratio, 4) * 100
#         }


if __name__ == '__main__':
    Path("./results/").mkdir(parents=True, exist_ok=True)
    uvicorn.run(app="s:app", host='0.0.0.0', port=65534, reload=True)
