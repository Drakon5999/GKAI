import torch
import numpy as np
from torchmetrics.detection.mean_ap import MeanAveragePrecision
from tqdm import tqdm


def train_one_epoch(model, device, optimizer, data_loader, print_freq, epoch):
    model.train()
    len_dataloader = data_loader.__len__()

    loss = 0
    iter_ = 0
    for imgs, annotations in data_loader:

        imgs = list(img.to(device) for img in imgs)
        annotations = [{k: v.to(device) for k, v in t.items()} for t in annotations]
        loss_dict = model(imgs, annotations)
        losses = sum(loss for loss in loss_dict.values())

        optimizer.zero_grad()
        losses.backward()
        optimizer.step()

        if iter_ % print_freq == 0:
            print(f'Epoch {epoch}. Iteration: {iter_}/{len_dataloader}, Loss: {losses}')

        loss += losses
        iter_ += 1

    epoch_loss = np.round(loss.data.cpu().numpy() / iter_, 4)
    print(f"Epoch {epoch} finised. Loss: {epoch_loss}")


@torch.inference_mode()
def evaluate(model,
             dl,
             device,
             iou_thresholds=(0.5),
             max_detection_thresholds=(50, 100, 200),
             filter_fn=None):
    model.eval()
    metric = MeanAveragePrecision(class_metrics=True,
                                  iou_thresholds=iou_thresholds,
                                  max_detection_thresholds=max_detection_thresholds)
    support = dict()
    for images, targets in tqdm(dl):
        images = list(img.to(device) for img in images)

        # calculating support
        for t in targets:
            for l in t['labels']:
                key = int(l.item())
                support[key] = support.get(key, 0) + 1

        outputs = model(images)

        if filter_fn is not None:
            outputs = filter_fn(outputs)

        targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
        metric.update(outputs, targets)

    result = metric.compute()
    result['support'] = support

    return result
