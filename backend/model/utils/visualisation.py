import os

import numpy as np
import matplotlib.pyplot as plt
import json
from IPython.display import clear_output
import cv2
from PIL import Image
import torchvision
import torch


def viz_bbox(plt_img, bboxes, labels, class_names):
    """
    Draw bbox on image
    """
    k = 0
    if len(bboxes) != 0:
        for x1, y1, x2, y2 in bboxes:
            l = labels[k]
            k += 1
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            pl1 = plt_img[..., 0]
            pl2 = plt_img[..., 1]
            pl3 = plt_img[..., 2]
            img1 = cv2.rectangle(pl1, (x1, y1), (x2, y2), color=(0, 0, 0), thickness=3)
            img2 = cv2.rectangle(pl2, (x1, y1), (x2, y2), color=(1, 1, 1), thickness=3)
            cv2.putText(img2, class_names[l], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (1, 1, 1), 2)
            img3 = cv2.rectangle(pl3, (x1, y1), (x2, y2), color=(0, 0, 0), thickness=3)
            pl1_ = img1.reshape(img1.shape[0], img1.shape[1], 1)
            pl2_ = img2.reshape(img2.shape[0], img2.shape[1], 1)
            pl3_ = img3.reshape(img3.shape[0], img3.shape[1], 1)
            result = np.concatenate((pl1_, pl2_, pl3_), axis=2)
        return result
    else:
        return plt_img


def inference(model, device, data_loader, threshold, class_names):
    """
    Inference function for Jupyter notebook
    Draws gt and predicted bboxes
    """
    model.eval()

    for imgs, annotations in data_loader:

        imgs = list(img.to(device) for img in imgs)
        annotations = [{k: v.to(device) for k, v in t.items()} for t in annotations]
        gt_bbox = annotations[0]["boxes"].detach().cpu().numpy()
        gt_labels = annotations[0]["labels"].detach().cpu().numpy()

        output = model(imgs, annotations)

        bboxes = []
        pred_labels = []
        labels = output[0]['labels'].detach().cpu().numpy()
        for num, score in enumerate(output[0]['scores']):
            score = float(score.detach().cpu())
            if score > threshold:
                bboxes.append(list(map(int, output[0]['boxes'][num].detach().cpu().numpy())))
                pred_labels.append(labels[num])
        img = np.moveaxis(imgs[0].detach().cpu().numpy(), 0, 2)
        truth_img = viz_bbox(img, gt_bbox, gt_labels, class_names)
        img = np.moveaxis(imgs[0].detach().cpu().numpy(), 0, 2)
        pred_img = viz_bbox(img, bboxes, pred_labels, class_names)

        fig, (ax0, ax1) = plt.subplots(nrows=1, ncols=2, figsize=(18, 8))
        ax0.set_title('Ground Truth')
        ax0.imshow(truth_img)
        ax1.set_title('Prediction')
        ax1.imshow(pred_img)
        plt.show()

        x = input()
        clear_output()


def img_inference(model, device, img, threshold, class_names, out_dir=None):
    """
    Creates new image and json with detections based on model results
    """
    model.eval()
    if isinstance(img, str):
        img = Image.open(img)
    img = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])(img)
    output = model(torch.unsqueeze(img, dim=0).to(device))

    bboxes = []
    pred_labels = []
    labels = output[0]['labels'].detach().cpu().numpy()
    for num, score in enumerate(output[0]['scores']):
        score = float(score.detach().cpu())
        if score > threshold:
            bboxes.append(list(map(int, output[0]['boxes'][num].detach().cpu().numpy())))
            pred_labels.append(labels[num])
    img = np.moveaxis(img.numpy(), 0, 2)
    pred_img = viz_bbox(img, bboxes, pred_labels, class_names)
    meta = output[0]
    for k in meta.keys():
        meta[k] = meta[k].detach().cpu().numpy().tolist()
    if out_dir:
        plt.imsave(os.path.join(out_dir, os.path.basename(image_path)), pred_img)
        with open(os.path.join(out_dir, os.path.basename(image_path).split('.')[0] + '.json'), 'w') as f:
            json.dump(meta, f)
    else:
        return pred_img, meta
