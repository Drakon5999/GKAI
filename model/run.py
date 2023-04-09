import argparse

import torch
import torchvision
from pycocotools.coco import COCO

from utils.visualisation import *

parser = argparse.ArgumentParser(description='Train script for detection model')
parser.add_argument('--image_path', help='Path to image', type=str, required=True)
parser.add_argument('--num_classes', help='Number of classes', type=int, default=91)
parser.add_argument('--nms_thresh', help='Non Maximum Suppression threshold', type=float, default=0.2)
parser.add_argument('--thresh', help='Threshold parameter', type=float, default=0.5)
parser.add_argument('--path_to_model', help='Path to existing checkpoint', type=str, required=True)
parser.add_argument('--image_save_path', help='Path to dir for saving image with detections', type=str, default='./results/')
parser.add_argument('--annotations_path', help='Path to annotations with class_names', type=str, required=True)

if __name__ == "__main__":
    args = parser.parse_args()

    coco = COCO(args.annotations_path)
    cls = ['background'] + [coco.cats[i]['name'] if i in coco.cats.keys() else 'No class' for i in
                            range(1, max(coco.cats.keys()) + 1)]

    device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(box_nms_thresh=args.nms_thresh,
                                                                 num_classes=args.num_classes)
    model.load_state_dict(torch.load(args.path_to_model))
    model.to(device)

    img_inference(model, device, args.image_path, args.thresh, cls, args.image_save_path)

    print(f'Inference finished! Image and meta saved at {args.image_save_path}')
