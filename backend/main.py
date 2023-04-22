"""
Entry point for GKAI app
"""

from uuid import UUID, uuid4
import uvicorn
from fastapi import FastAPI, File, BackgroundTasks, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from PIL import Image
import io

from models import Job, JobStatus, Model
from classes import CLASS_NAMES

model = Model(model_path="./faster-rcnn-coco-v_2.pth", nms_threshold=0.2, threshold=0.5, class_names=CLASS_NAMES)

app = FastAPI()
job_mapping = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def process_job(new_job: Job):
    new_job.status = JobStatus.PROCESSING
    try:
        new_job.result_image, new_job.result = model.process_image(new_job.image)
        new_job.status = JobStatus.DONE
    except Exception as e:
        new_job.status = JobStatus.ERROR
        new_job.error_message = str(e)
        raise e


def check_uuid(job_id):
    if job_id not in job_mapping:
        raise HTTPException(status_code=404, detail="Incorrect UUID")


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
- - - - Возможные значения: DONE, WAITING, PROCESSING, ERROR (в случае error возвращается описание ошибки)

- - GET /job_result?job_id=<...>
- - - Принимает job_id
- - - Возвращает json с результатами разметки

- - GET /job_result_visualisation?job_id=<...>
- - - Принимает job_id
- - - Возвращает картинку с разметкой (не в json, а с типом image/png)
"""


@app.post('/add_job')
async def add_job(bg_task: BackgroundTasks, image: UploadFile = File(...)) -> dict:
    """
    Endpoint for **upload image**\n
    * body **image**\n
    * return **json**
    """
    uid = uuid4()
    img = Image.open(io.BytesIO(await image.read()))
    new_job = Job(uuid=uid, status=JobStatus.NEW, image=img)
    job_mapping[uid] = new_job
    bg_task.add_task(process_job, new_job)
    return {'job_id': str(uid)}


@app.get('/job_status')
async def job_status(job_id: UUID) -> dict:
    """
    Endpoint for **find out the status** by job_id\n
    * param **job_id**\n
    * return **json**
    """
    check_uuid(job_id)
    # result = {"status": job_mapping[job_id].status, "error_message": job_mapping[job_id].error_message}
    # if job_mapping[job_id].error_message is not None:
    #     result["error_message"] = job_mapping[job_id].error_message
    return {"status": job_mapping[job_id].status, "error_message": job_mapping[job_id].error_message}



@app.get('/job_result')
async def job_result(job_id: UUID) -> dict:
    """
    Endpoint for **get computed bounding boxes** by job_id\n
    * param **job_id**\n
    * return **json**
    """
    check_uuid(job_id)
    return {"result": job_mapping[job_id].result}


@app.get("/job_result_visualisation")
async def job_result_visualisation(job_id: UUID) -> StreamingResponse:
    """
    Endpoint for **get an image with bounding boxes on it** by job_id\n
    * param **job_id**\n
    * return **image**
    """
    check_uuid(job_id)
    return StreamingResponse(io.BytesIO(job_mapping[job_id].result_image), media_type="image/png")


def main():
    """
    Main function
    """
    uvicorn.run(app, host='127.0.0.1', port=8800)


if __name__ == '__main__':
    main()
