import os
from pathlib import Path
import subprocess
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


def get_directory_size_fast(directory):
    """Get directory size using system command for faster performance."""
    try:
        result = subprocess.check_output(['du', '-s', directory])
        return int(result.split()[0].decode('utf-8')) * 1024  # du returns size in kilobytes
    except Exception as e:
        return str(e)


def convert_bytes(byte_size):
    """Convert bytes to a more readable format."""
    units = ['B', 'KB', 'MB', 'GB', 'TB']

    unit_index = 0
    while byte_size > 1024 and unit_index < len(units) - 1:
        byte_size /= 1024.0
        unit_index += 1

    result = f"{byte_size:.2f} {units[unit_index]}"
    return result


def count_small_files(directory, max_size_kb):
    """Count files smaller than a certain size using the 'find' command."""
    try:
        # Constructing the find command
        command = ['find', directory, '-type', 'f', '-size', f'-{max_size_kb}k', '|', 'wc', '-l']
        result = subprocess.check_output(' '.join(command), shell=True)
        return int(result.strip())
    except Exception as e:
        return str(e)


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


@app.get("/list/complete") 
async def get_complete_list():
    """Get a list of completed files."""
    file_list = [int(file.stem) for file in Path('./results').glob('*.json')]
    return file_list


@app.get("/info")
async def get_info():
    """Get information about the current state of the server."""
    completion_num = len(await get_complete_list())
    less_than_1kb = count_small_files('./results', 1)
    less_than_1kb_ratio = less_than_1kb / completion_num

    return {
        'completion_num': completion_num,
        'completion_size': convert_bytes(get_directory_size_fast('./results')),
        'less_than_1kb': less_than_1kb,
        'less_than_1kb_ratio': round(less_than_1kb_ratio, 4) * 100
        }


if __name__ == '__main__':
    Path("./results/").mkdir(parents=True, exist_ok=True)
    uvicorn.run(app="main:app", host='0.0.0.0', port=65534, reload=True, workers=2)
