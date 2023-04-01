"""
Entry point for GKAI app
"""

from uuid import UUID, uuid4
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

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
async def add_job(image: UploadFile = File(...)) -> dict:
    """
    Endpoint for **upload image**\n
    * body **image**\n
    * return **json**
    """
    uid = uuid4()

    return {'job_id': str(uid)}


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


def main():
    """
    Main function
    """
    uvicorn.run(app, host='127.0.0.1', port=8800)


if __name__ == '__main__':
    main()
