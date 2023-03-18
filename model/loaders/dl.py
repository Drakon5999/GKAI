"""
Dataloader for COCO format
"""
import os
import torch
from PIL import Image
from pycocotools.coco import COCO
import torchvision
from math import floor


def collate_fn(batch):
    return tuple(zip(*batch))


class COCODataset(torch.utils.data.Dataset):
    def __init__(self, root, annotation, transforms=None):
        self.root = root
        self.transforms = transforms
        self.coco = COCO(annotation)
        self.ids = list(sorted(self.coco.imgs.keys()))

    def __getitem__(self, index):
        coco = self.coco
        img_id = self.ids[index]
        # Ann is for "annotation"
        ann_ids = coco.getAnnIds(imgIds=img_id)
        coco_annotation = coco.loadAnns(ann_ids)
        path = coco.loadImgs(img_id)[0]['file_name']
        img = Image.open(os.path.join(self.root, path))

        num_objs = len(coco_annotation)

        boxes = []
        labels = []
        # COCO has coordinates in format [xmin, ymin, width, height]
        # Torch needs format [xmin, ymin, xmax, ymax]
        for i in range(num_objs):
            xmin = floor(coco_annotation[i]['bbox'][0])
            ymin = floor(coco_annotation[i]['bbox'][1])
            xmax = floor(xmin + coco_annotation[i]['bbox'][2])
            ymax = floor(ymin + coco_annotation[i]['bbox'][3])
            # There are some detections with zero width or height
            if ymax == ymin:
                ymax += 1
            if xmax == xmin:
                xmax += 1

            boxes.append([xmin, ymin, xmax, ymax])
            labels.append(coco_annotation[i]['category_id'])

        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)
        img_id = torch.tensor([img_id])
        areas = []
        for i in range(num_objs):
            areas.append(coco_annotation[i]['area'])

        areas = torch.as_tensor(areas, dtype=torch.float32)
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)
        # Creating annotation for model
        annotation = dict({})
        annotation["boxes"] = boxes
        annotation["labels"] = labels
        annotation["image_id"] = img_id
        annotation["area"] = areas
        annotation["iscrowd"] = iscrowd

        img = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])(img)

        return img, annotation

    def __len__(self):
        return len(self.ids)
