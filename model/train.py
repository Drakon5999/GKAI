import os
import argparse

import torch
import torchvision
from pycocotools.coco import COCO

from utils.prepare_dataset import clean_zero
from loaders.dl import COCODataset, collate_fn
from models.train_utils import *

parser = argparse.ArgumentParser(description='Train script for detection model')
parser.add_argument('--images_path', help='Directory with images', type=str, required=True)
parser.add_argument('--annotations_path', help='Directory with annotations', type=str, required=True)
parser.add_argument('--remove_zeros', help='Delete annotations with no objects', type=bool, default=True)
parser.add_argument('--train_batch_size', help='Batch size for train', type=int, default=8)
parser.add_argument('--test_batch_size', help='Batch size for test', type=int, default=8)
parser.add_argument('--num_classes', help='Number of classes', type=int, default=91)
parser.add_argument('--nms_thresh', help='Non Maximum Suppression threshold', type=float, default=0.2)
parser.add_argument('--num_epochs', help='Number of epochs for train', type=int, default=10)
parser.add_argument('--path_to_model', help='Path to existing checkpoint', type=str, default=None)
parser.add_argument('--model_save_path', help='Path to dir for saving checkpoints', type=str, default='./checkpoints/detector.pth')
parser.add_argument('--lr', help='Learning rate', type=float, default=0.005)
parser.add_argument('--momentum', help='Momentum', type=float, default=0.9)
parser.add_argument('--weight-decay', help='Weight decay', type=float, default=0.0005)
parser.add_argument('--print_freq', help='Print frequency', type=int, default=25)

if __name__ == "__main__":
    args = parser.parse_args()

    if args.remove_zeros:
#         clean_zero(os.path.join(args.annotations_path, 'train.json'))
#         clean_zero(os.path.join(args.annotations_path, 'val.json'))
        train_annotations = os.path.join(args.annotations_path, 'train_clean.json')
        val_annotations = os.path.join(args.annotations_path, 'val_clean.json')
    else:
        train_annotations = os.path.join(args.annotations_path, 'train.json')
        val_annotations = os.path.join(args.annotations_path, 'val.json')

    coco = COCO(val_annotations)
    cls = ['background'] + [coco.cats[i]['name'] if i in coco.cats.keys() else 'No class' for i in range(1, max(coco.cats.keys()) + 1)]

    train_ds = COCODataset(root=args.images_path,
                           annotation=val_annotations)

    test_ds = COCODataset(root=args.images_path,
                          annotation=val_annotations)

    data_loader_train = torch.utils.data.DataLoader(train_ds,
                                                    batch_size=args.train_batch_size,
                                                    shuffle=True,
                                                    num_workers=4,
                                                    collate_fn=collate_fn)

    data_loader_test = torch.utils.data.DataLoader(test_ds,
                                                   batch_size=args.test_batch_size,
                                                   shuffle=True,
                                                   num_workers=4,
                                                   collate_fn=collate_fn)

    device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(box_nms_thresh=args.nms_thresh,
                                                                 num_classes=args.num_classes)
    if args.path_to_model:
        model.load_state_dict(torch.load(args.path_to_model))
    model.to(device)

    best_metric = 0
    print_freq = args.print_freq

    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, lr=args.lr, momentum=args.momentum, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.25)

    for epoch in range(1, args.num_epochs):

        train_one_epoch(model, device, optimizer, data_loader_train, print_freq, epoch)
        current_metric = evaluate(model=model, dl=data_loader_test, device=device, iou_thresholds=[0.5],
                                  max_detection_thresholds=[50, 100, 200], filter_fn=None)
        print('mAP: ', current_metric['map'].item())
        if current_metric['map'].item() > best_metric:
            torch.save(model.state_dict(), args.path_to_model)
            best_metric = current_metric['map'].item()

        scheduler.step()

    print(f'Train finished! Best checkpoint saved at {args.model_save_path}')
