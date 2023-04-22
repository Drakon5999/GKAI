from dataclasses import dataclass
from typing import Optional

import matplotlib.pyplot as plt
import torch
import torchvision
from enum import Enum
from uuid import UUID
from PIL import Image
import io

from model.utils.visualisation import img_inference


class JobStatus(str, Enum):
    DONE = "DONE"
    ERROR = "ERROR"
    PROCESSING = "PROCESSING"
    NEW = "NEW"


@dataclass
class Job:
    """Class for keeping track of an item in inventory."""
    uuid: UUID
    image: Image
    status: JobStatus = JobStatus.NEW
    result: Optional[dict] = None
    result_image: Optional[Image.Image] = None


class Model:
    def __init__(self, model_path: str, nms_threshold: float, threshold: float, class_names: list):
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(box_nms_thresh=nms_threshold,
                                                                          num_classes=len(class_names),
                                                                          weights=None)
        self.model = self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
        self.threshold = threshold
        self.class_names = class_names

    def process_image(self, image: Image):
        img, result_json = img_inference(self.model, self.device, image, self.threshold, self.class_names)
        with io.BytesIO() as buffer:  # use buffer memory
            plt.imsave(buffer, img)
            buffer.seek(0)
            image = buffer.getvalue()
        return image, result_json
