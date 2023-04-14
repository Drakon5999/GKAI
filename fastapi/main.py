"""
Entry point for GKAI app
"""

from uuid import UUID, uuid4
from uvicorn import Server, Config
from fastapi import FastAPI, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from queue import Queue
from dataclasses import dataclass
from enum import Enum
import asyncio

class JobStatus(str, Enum):
    DONE = "DONE"
    ERROR = "ERROR"
    PROCESSING = "PROCESSING"
    NEW = "NEW"

ochered = Queue()
app = FastAPI()

@dataclass
class Job:
    """Class for keeping track of an item in inventory."""
    uuid: UUID
    status: JobStatus = JobStatus.NEW
    image: UploadFile
    result: dict = {}
    result_image: File


job_mapping = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def root():
    """
    Endpoint for a **root path**\n
    * return **json**
    """
    return {"message": "Welcome to GKAI API"}


"""
- Создать 4 эндпоинта:
- - POST /add_job
- - - Принимает картинку в формате  multipart form data
- - - Возвращает json с одним полем job_id, типа строка

- - GET /job_status?job_id=<...>
- - - Принимает job_id
- - - Возвращает json с одним полем status, типа строка
- - - - Возможные значения: DONE, WAITING, PROCESSING, ERROR (в случае error кидать ещё описание ошибки)

- - GET /job_result?job_id=<...>
- - - Принимает job_id
- - - Возвращает json с результатами разметки

- - GET /job_result_visualisation?job_id=<...>
- - - Принимает job_id
- - - Возвращает картинку с разметкой (не в json, а прям с типом image/...)
"""


@app.post('/add_job')
async def add_job(job_mapper: dict, image: UploadFile, bg_task: BackgroundTasks) -> dict:
    """
    Endpoint for **upload image**\n
    * body **image**\n
    * return **json**
    """
    uid = uuid4()
    new_job = Job(uuid=uid, status=JobStatus.NEW, image=image)
    job_mapping[uid] = new_job
    bg_task.add_task(process_job, new_job)
    return {'job_id': str(uid)}

def process_job(new_job: Job):
    new_job.status = JobStatus.PROCESSING



@app.get('/job_status')
async def job_status(job_id: UUID) -> dict:
    """
    Endpoint for **find out the status** by job_id\n
    * param **job_id**\n
    * return **json**
    """
    if job_id == UUID('a51851dd-7109-41e8-9e6b-8ad89cf8ada3'):
        return {f'status for job {job_id}': 'DONE'}
    elif job_id == UUID('a51851dd-7109-41e8-9e6b-8ad89cf8ada2'):
        error_description = 'why did this happen?'
        return {f'status for job {job_id}': 'ERROR', 'description': error_description}

    return {f'status for job {job_id}': 'PROCESSING'}


@app.get('/job_result')
async def job_result(job_id: UUID) -> dict:
    """
    Endpoint for **get computed bounding boxes** by job_id\n
    * param **job_id**\n
    * return **json**
    """

    return {'bounding_box_1': [100.0, 20.5, 10.2, 21.3], 'bounding_box_2': [13.3, 1.5, 99.2, 28.7]}


@app.get("/job_result_visualisation")
async def job_result_visualisation(job_id: UUID) -> FileResponse:
    """
    Endpoint for **get an image with bounding boxes on it** by job_id\n
    * param **job_id**\n
    * return **image**
    """
    return FileResponse('test_file')

async def periodic():
    while True:
        print('periodic')
        await asyncio.sleep(1)

def stop():
    task.cancel()

def main():
    """
    Main function
    """
    asyncio.get_running_loop()
    loop = asyncio.new_event_loop()
    config = Config(app=app, loop=loop, host='127.0.0.1', port=8800)
    server = Server(config)
    task = loop.create_task(periodic())
    loop.run_until_complete(server.serve())
    stop()


if __name__ == '__main__':
    main()
