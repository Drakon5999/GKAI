"""
Entry point for GKAI app
"""

from uuid import UUID, uuid4
import uvicorn
from fastapi import FastAPI, File, BackgroundTasks, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

from models import Job, JobStatus, Model

class_names = ['background',
               'person',
               'bicycle',
               'car',
               'motorcycle',
               'airplane',
               'bus',
               'train',
               'truck',
               'boat',
               'traffic light',
               'fire hydrant',
               'No class',
               'stop sign',
               'parking meter',
               'bench',
               'bird',
               'cat',
               'dog',
               'horse',
               'sheep',
               'cow',
               'elephant',
               'bear',
               'zebra',
               'giraffe',
               'No class',
               'backpack',
               'umbrella',
               'No class',
               'No class',
               'handbag',
               'tie',
               'suitcase',
               'frisbee',
               'skis',
               'snowboard',
               'sports ball',
               'kite',
               'baseball bat',
               'baseball glove',
               'skateboard',
               'surfboard',
               'tennis racket',
               'bottle',
               'No class',
               'wine glass',
               'cup',
               'fork',
               'knife',
               'spoon',
               'bowl',
               'banana',
               'apple',
               'sandwich',
               'orange',
               'broccoli',
               'carrot',
               'hot dog',
               'pizza',
               'donut',
               'cake',
               'chair',
               'couch',
               'potted plant',
               'bed',
               'No class',
               'dining table',
               'No class',
               'No class',
               'toilet',
               'No class',
               'tv',
               'laptop',
               'mouse',
               'remote',
               'keyboard',
               'cell phone',
               'microwave',
               'oven',
               'toaster',
               'sink',
               'refrigerator',
               'No class',
               'book',
               'clock',
               'vase',
               'scissors',
               'teddy bear',
               'hair drier',
               'toothbrush']

model = Model(model_path="./faster-rcnn-coco-v_2.pth", nms_threshold=0.2, threshold=0.5, class_names=class_names)

app = FastAPI()
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
- - POST /adda_job
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
async def add_job(job_mapping: dict, bg_task: BackgroundTasks, image: UploadFile = File(...)) -> dict:
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


def process_job(new_job: Job):
    new_job.status = JobStatus.PROCESSING
    new_job.result_image, new_job.result = model.process_image(new_job.image)


@app.get('/job_status')
async def job_status(job_id: UUID) -> dict:
    """
    Endpoint for **find out the status** by job_id\n
    * param **job_id**\n
    * return **json**
    """
    return {"status": job_mapping[job_id].status}


@app.get('/job_result')
async def job_result(job_id: UUID) -> dict:
    """
    Endpoint for **get computed bounding boxes** by job_id\n
    * param **job_id**\n
    * return **json**
    """

    return {"result": job_mapping[job_id].result}


@app.get("/job_result_visualisation")
async def job_result_visualisation(job_id: UUID) -> FileResponse:
    """
    Endpoint for **get an image with bounding boxes on it** by job_id\n
    * param **job_id**\n
    * return **image**
    """
    return job_mapping[job_id].result_image


def main():
    """
    Main function
    """
    uvicorn.run(app, host='127.0.0.1', port=8800)


if __name__ == '__main__':
    main()
