import json


def clean_zero(path):
    with open(path) as f:
        d2 = json.load(f)

    list_of_img_id = []
    for img in d2['images']:
        list_of_img_id.append(img['id'])

    useful_image = []
    for img in d2['annotations']:
        useful_image.append(img['image_id'])

    new_images = []
    for img in d2['images']:
        if img['id'] in useful_image:
            new_images.append(img)

    old_index = -1
    new_index = 0
    dict_img = {}

    for index in useful_image:
        if old_index != index:
            dict_img[index] = new_index
            old_index = index
            new_index += 1

    for img in new_images:
        img['id'] = dict_img[img['id']]

    d2["images"] = new_images

    for ann in d2['annotations']:
        ann['image_id'] = dict_img[ann['image_id']]

    with open(path.replace('.json', '_clean.json'), 'w') as f:
        json.dump(d2, f)
